#!/usr/bin/python3
# coding: utf-8

# dropip.py
# 2023.10.08 version 2.0.2 new option 'validity'
# 2023.09.29 version 2.0.1 new option 'mailto'
# 2023.09.13 version 2.0
# -----------------------------------------------------------------------------

import os
import sys
import re
import sqlite3
from datetime import datetime, timedelta
import socket

# default
config = {
    'server':'apache',          # apache or nginx
    'accesslog':'/var/log/httpd/access_log',    # full path of access log
    'outfile':'./deny.conf',    # output file
    'threshold':10,             # threshold of error(4xx 5xx) count
    'validity':0,               # validity (0:None)
    'hostname':socket.gethostname(),
    'mailto':'',
}

for i in range(len(sys.argv)):
    if sys.argv[i][0:1] != '-':
        continue
    if '-h' in sys.argv or '--help' in sys.argv:
        print("dropip.py [-s {apache|nginx}][-l FULLPATH_ACCESS_LOG][-o OUTPUT_FILE][-t (int)THRESHOLD]")
        sys.exit(0)
    elif sys.argv[i] == '-s' or sys.argv[i] == '--server':
        if sys.argv[i+1] != 'apache' and sys.argv[i+1] != 'nginx':
            print("Server type is 'apache' or 'nginx'")
            sys.exit(1)
        config['server'] = sys.argv[i+1]
    elif sys.argv[i] == '-l' or sys.argv[i] == '--log':
        config['accesslog'] = sys.argv[i+1]
    elif sys.argv[i] == '-o' or sys.argv[i] == '--outfile':
        config['outfile'] = sys.argv[i+1]
    elif sys.argv[i] == '-t' or sys.argv[i] == '--threshold':
        config['threshold'] = int(sys.argv[i+1])
    elif sys.argv[i] == '-v' or sys.argv[i] == '--validity':
        config['validity'] = int(sys.argv[i+1])
    elif sys.argv[i] == '-m' or sys.argv[i] == '--mailto':
        config['mailto'] = sys.argv[i+1]

now = datetime.today()
hiduke = now.strftime('%Y-%m-%d %H:%M:%S')

execlog = open('./exec.log', 'w')

if config['mailto']:
    outstr = 'From: dropip@' + config['hostname'] + '\n'
    execlog.write(outstr)
    outstr = 'To: ' + config['mailto'] + '\n'
    execlog.write(outstr)
    outstr = 'Subject: dropip ' + hiduke + '\n\n'
    execlog.write(outstr)

outstr = 'dropip ' + hiduke + '\n'
execlog.write(outstr)

outstr = 'log: ' + config['accesslog'] + '\n'
execlog.write(outstr)

# text to array
allowip = []
in_file = open('./allowip', 'r')
for instr in in_file:
    arr = instr.split('/')
    allowip.append(arr[0].strip())
in_file.close()

allowwords = []
in_file = open('./allowwords', 'r')
for instr in in_file:
    word = re.compile(instr.strip())
    allowwords.append(word)
in_file.close()

denywords = []
in_file = open('./denywords', 'r')
for instr in in_file:
    word = re.compile('('+instr.strip()+')')
    denywords.append(word)
in_file.close()

# DB
dbcon = sqlite3.connect('./dropip.db')
db = dbcon.cursor()
if os.path.getsize('./dropip.db') == 0:
    sql = "create table deny (`ip` text primary key, `code` text, `insdate` text)"
    db.execute(sql)
    dbcon.commit()

# Delete data that has passed its expiration date
if config['validity'] > 0:
    vp = now - timedelta(days=config['validity'])
    validity_period = vp.strftime('%Y-%m-%d %H:%M:%S')
    sql = "delete from deny where `insdate` < ?"
    db.execute(sql, (validity_period,))
    dbcon.commit()

#
passlog = open('./pass.log', 'w')
count_accesslog = {}

denied = ''
count_deny = 0

ptn_count = re.compile(r'\[(\d\d).+?[\+|\-]\d{4}\]\s".*?"\s(\d)\d\d\s')

# scan access log
try:
    accesslog = open(config['accesslog'])
except FileNotFoundError:
    print('Not exists '+config['accesslog'])
    sys.exit(1)

# seek accesslog
for instr in accesslog:
    [ip, logstr] = instr.strip().split(' ', 1)
    rtn = ptn_count.search(logstr)

    # allowed ip?
    if ip in allowip:
        # in DB?
        sql = "select `ip` from `deny` where `ip` = ?"
        db.execute(sql, (ip,))
        data = db.fetchone()

        if data:
            sql = "delete from `deny` where `ip` = ?"
            db.execute(sql, (ip,))
            dbcon.commit()

        continue

    # allow word?
    flag = 0
    for word in allowwords:
        if flag:
            break

        rtn = word.search(logstr)
        if rtn != None:
            sql = "delete from `deny` where `ip` = ?"
            db.execute(sql, (ip,))
            dbcon.commit()
            flag = 1
            break

    if ip == denied:
        continue

    # deny.ip 登録済み
    sql = "select `ip`from `deny`where `ip` = ?"
    db.execute(sql, (ip,))
    data = db.fetchone()
    if data != None:
        continue

    # deny word ?
    flag = 0
    for word in denywords:
        if flag:    # 登録済み
            break

        rtn = word.search(logstr)
        if rtn != None:
            code = rtn.group(1)
            sql = "insert into `deny` (`ip`, `code`,`insdate`) values (?, ?, ?)"
            db.execute(sql, (ip, code, hiduke,))
            dbcon.commit()

            outstr = ip + ': deny by ' + code + '\n'
            execlog.write(outstr)
            denied = ip     # 今回登録したip
            count_deny += 1
            flag = 1

    rtn = ptn_count.search(logstr)
    if rtn.group(2) == '4' or rtn.group(1) == '5':
        skey = rtn.group(1) + ' ' + ip

        if skey in count_accesslog:
            count_accesslog[skey] += 1
            if count_accesslog[skey] > config['threshold']:
                sql = "select `ip` from `deny` where `ip` = ?"
                db.execute(sql, (ip,))
                data = db.fetchone()

                if data == None:
                    sql = "insert into `deny` (`ip`, `code`, `insdate`) values (?, ?, ?)"
                    code = 'threshold(' + str(config['threshold']) + ')'
                    db.execute(sql, (ip, code, hiduke,))
                    dbcon.commit()

                    outstr = ip + ':deny (> ' + str(config['threshold']) + ')\n'
                    execlog.write(outstr)

                denied = ip
                count_deny += 1
        else:
            count_accesslog[skey] = 1

    denyed = ''
    passlog.write(instr)

accesslog.close()
passlog.close()

# count_accesslog
execlog.write('\n');
for k, v in count_accesslog.items():
    execlog.write(k + ': ' + str(v) + '\n')
execlog.close()

# write conf
conf = open(config['outfile'], 'w')

sql = "select `ip` from deny order by `ip`"
db.execute(sql)
arr = db.fetchall()
for item in arr:
    ip = item[0]
    if config['server'] == 'apache':
        outstr = 'deny from '+ip+'\n'
    else:
        outstr = 'deny '+ip+';\n'
    conf.write(outstr)

conf.close()
dbcon.close()

if count_deny:
    sys.exit(1)
else:
    sys.exit(0)
