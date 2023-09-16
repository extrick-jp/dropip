#!/bin/bash
cd /usr/local/bin/dropip
/bin/python3 ./dropip.py -s apache -l /var/log/httpd/access_log || {
    cat exec.log
}
cat ./foreign.ip ./deny.conf > ./htaccess
cp ./htaccess /var/www/SITE_NAME/html/.htaccess
