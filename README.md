# dropip
Deny the source of brute force attacks.

  version 2.x<br />
  copyright 2023. EXTRICK LLC.

■ What's dropip?<br />
  Webサーバーのアクセスログをスキャンして、不審なアクセス元のIPを探し出し、.htaccessに登録して今後のアクセスを拒否するツールです。
  ブルートフォースアタックを有効にブロックします。

■ Composition<br />
  dropip.py       本体スクリプト<br />
  denywords       拒否する単語を登録しておきます<br />
  allowip         許可するIPを登録しておきます。<br />
  allowwords      許可する単語を登録しておきます<br />


■ Options<br />
  dropip.py -h または dropip.py --help で表示されます。<br />
  -s --server     apache または nginx を指定します。（apache）<br />
  -l --accesslog  スキャンするログファイルを指定します。（/var/log/httpd/access_log）<br />
  -o --outfile    出力するファイルを指定します。（./deny.conf）<br />
  -i --insertfile 出力するファイルに挿入するファイルを指定します。<br />
  -t --threshold  エラー（4xx、5xx）をカウントして拒否する閾値を指定します。（10）<br />


■ Install & Usage<br />
  cron で定期的に実行することを想定しています。<br />
  適当な場所にファイル一式をコピーします。<br />
  例：<br />
  /usr/local/bin/dropip/<br />
    +-- dropip.py<br />
    +-- allowip<br />
    +-- allowwords<br />
    +-- denywords<br />

  allowip<br />
    ここに記載されたIPは無条件にアクセスを許可します。<br />
    サーバー管理者のIPなどを登録しておきます。<br />

  allowwords<br />
    ここに記載された文字列を含むアクセスは無条件に許可されます。<br />
    正規表現で記述します。（後述）<br />

  denywords<br />
    ここに記載された文字列を含むアクセスのアクセス元IPは拒否リストに登録されます。<br />
    以降、拒否リストに登録されたIPからは、すべてのアクセスを拒否します。<br />
    正規表現で記述します。（後述）<br />

  実行後に生成されるファイル<br />
    dropip.db   拒否IPを格納しているSQLite3データベース<br />
    deny.conf   .htaccess（for apache）、nginx confファイル（for nginx）<br />
    exec.log    今回の実行で拒否したIPと、日別のエラーカウントのリスト<br />
    pass.log    今回の実行で拒否されなかったアクセスログ<br />


■ Execution<br />
  実際に運用する際は、次のようなバッチファイルを cron に登録すると管理が楽になります。<br />

  apache の場合<br />
    dropip.sh を作成します。<br />

    #!/bin/bash
    DROPIP_PATH="/usr/local/bin/dropip"
    /bin/python3 $DROPIP_PATH/dropip.py -s apache -l /var/log/httpd/access_log
    cat exec.log
    cp $APP_PATH/deny.conf /var/www/SITE_NAME/html/.htaccess

    crontab に dropip.sh を登録します。

    DROPIP_PATH=/usr/local/bin/dropip
    51 * * * * /usr/bin/python3 $DROPIP_PATH/dropip.sh

  nginx の場合<br />
    dropip.sh を作成します。<br />
    拒否リストを出力後、nginx をリロードする必要があります。<br />

    #!/bin/bash
    DROPIP_PATH="/usr/local/bin/dropip"
    /bin/python3 $DROPIP_PATH/dropip.py -s nginx -l /var/log/httpd/access_log
    cat exec.log
    systemctl reload nginx

    crontab に dropip.sh を登録します。

    DROPIP_PATH=/usr/local/bin/dropip
    51 * * * * /usr/bin/python3 $DROPIP_PATH/dropip.sh

    出力ファイル（deny.conf）を nginx の設定ファイルとして読み込むように設定しておきます。
    例： ln -s /usr/local/bin/dropip/deny.conf /etc/nginx/conf.d/deny.conf

  いずれも、exec.log を標準出力に出力して、メールで結果が届くようにしています。<br />
  pass.log を開いて、怪しいアクセスを探してください。<br />
  あるはずのないディレクトリやファイルへのアクセスはブルートフォースアタックの可能性があります。キーワードとして正規表現（後述）で  denywords に追加しておきましょう。<br />


■ How to<br />
  apache で wordpress が生成した .htaccess があるなど、予め設定した .htaccess がある場合は、.htaccess をリネーム（例：.htaccess.x）しておき、オプション -i で読み込むようにします。出力ファイル（deny.conf）に拒否リストを出力する前に、.htaccess.x の内容を出力します。<br />
  例：<br />
  dropip.py -i .htaccess.x<br />

  予めダウンロードした海外のIPリスト（foreign_ip.conf）などがある場合は、オプション -i で読み込むことで、海外のIPリストと dropip が出力した拒否リストを一つのファイルにまとめることができます。<br />
  例：<br />
  dropip.py -i foreign_ip.conf<br />

  cat コマンドを使って、dropip.py の出力ファイル（deny.conf）に設定済みのファイルを結合しても構いません。<br />
  例：<br />
  cat .htaccess.x deny.conf foreign_ip.conf > .htaccess<br />


■ 正規表現<br />
  allowwords、denywords に記述する正規表現は、'/' 以外のメタ文字を '\' でエスケープした文字列です。<br />
  例："GET /class.api.php を拒否する場合<br />
    denywords には、"GET /class\.api\.php を登録します。<br />


■ 更新履歴<br />
  version 2.0 2023.09.13<br />
    以前の php cli版を python3 で書き換えて公開しました。<br />
