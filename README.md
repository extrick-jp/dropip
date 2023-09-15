# dropip
Deny the source of brute force attacks.

  version 2.x<br />
  copyright 2023. EXTRICK LLC.

■ What's dropip?
  Webサーバーのアクセスログをスキャンして、不審なアクセス元のIPを探し出し、.htaccessに登録して今後のアクセスを拒否するツールです。
  ブルートフォースアタックを有効にブロックします。

■ Composition
  dropip.py       本体スクリプト
  denywords       拒否する単語を登録しておきます
  allowip         許可するIPを登録しておきます。
  allowwords      許可する単語を登録しておきます


■ Options
  dropip.py -h または dropip.py --help で表示されます。
  -s --server     apache または nginx を指定します。（apache）
  -l --accesslog  スキャンするログファイルを指定します。（/var/log/httpd/access_log）
  -o --outfile    出力するファイルを指定します。（./deny.conf）
  -i --insertfile 出力するファイルに挿入するファイルを指定します。
  -t --threshold  エラー（4xx、5xx）をカウントして拒否する閾値を指定します。（10）


■ Install & Usage
  cron で定期的に実行することを想定しています。
  適当な場所にファイル一式をコピーします。
  例：
  /usr/local/bin/dropip/
    +-- dropip.py
    +-- allowip
    +-- allowwords
    +-- denywords

  allowip
    ここに記載されたIPは無条件にアクセスを許可します。
    サーバー管理者のIPなどを登録しておきます。

  allowwords
    ここに記載された文字列を含むアクセスは無条件に許可されます。
    正規表現で記述します。（後述）

  denywords
    ここに記載された文字列を含むアクセスのアクセス元IPは拒否リストに登録されます。
    以降、拒否リストに登録されたIPからは、すべてのアクセスを拒否します。
    正規表現で記述します。（後述）

  実行後に生成されるファイル
    dropip.db   拒否IPを格納しているSQLite3データベース
    deny.conf   .htaccess（for apache）、nginx confファイル（for nginx）
    exec.log    今回の実行で拒否したIPと、日別のエラーカウントのリスト
    pass.log    今回の実行で拒否されなかったアクセスログ


■ Execution
  実際に運用する際は、次のようなバッチファイルを cron に登録すると管理が楽になります。

  apache の場合
    dropip.sh を作成します。

    #!/bin/bash
    DROPIP_PATH="/usr/local/bin/dropip"
    /bin/python3 $DROPIP_PATH/dropip.py -s apache -l /var/log/httpd/access_log
    cat exec.log
    cp $APP_PATH/deny.conf /var/www/SITE_NAME/html/.htaccess

    crontab に dropip.sh を登録します。

    DROPIP_PATH=/usr/local/bin/dropip
    51 * * * * /usr/bin/python3 $DROPIP_PATH/dropip.sh

  nginx の場合
    dropip.sh を作成します。
    拒否リストを出力後、nginx をリロードする必要があります。

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

  いずれも、exec.log を標準出力に出力して、メールで結果が届くようにしています。
  pass.log を開いて、怪しいアクセスを探してください。
  あるはずのないディレクトリやファイルへのアクセスはブルートフォースアタックの可能性があります。キーワードとして正規表現（後述）で  denywords に追加しておきましょう。


■ How to
  apache で wordpress が生成した .htaccess があるなど、予め設定した .htaccess がある場合は、.htaccess をリネーム（例：.htaccess.x）しておき、オプション -i で読み込むようにします。出力ファイル（deny.conf）に拒否リストを出力する前に、.htaccess.x の内容を出力します。
  例：
  dropip.py -i .htaccess.x

  予めダウンロードした海外のIPリスト（foreign_ip.conf）などがある場合は、オプション -i で読み込むことで、海外のIPリストと dropip が出力した拒否リストを一つのファイルにまとめることができます。
  例：
  dropip.py -i foreign_ip.conf

  cat コマンドを使って、dropip.py の出力ファイル（deny.conf）に設定済みのファイルを結合しても構いません。
  例：
  cat .htaccess.x deny.conf foreign_ip.conf > .htaccess


■ 正規表現
  allowwords、denywords に記述する正規表現は、'/' 以外のメタ文字を '\' でエスケープした文字列です。
  例："GET /class.api.php を拒否する場合
    denywords には、"GET /class\.api\.php を登録します。


■ 更新履歴
  version 2.0 2023.09.13
    以前の php cli版を python3 で書き換えて公開しました。
