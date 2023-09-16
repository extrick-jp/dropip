<?php
/*
    console.php
    for dropip
-------------------------------------------------------------------------------*/
ini_set('display_errors', 'On');

$config = array(
    'dropip_path' => '/usr/local/bin/dropip',
);

?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="format-detection" content="telephone=no">
<link href="./style.css" rel="stylesheet" type="text/css" />
<script src="https://code.jquery.com/jquery-3.6.3.min.js" integrity="sha256-pvPw+upLPUjgMXY0G+8O0xUf+/Im1MZjXxxgOcBQBXU=" crossorigin="anonymous"></script>
<script src="./js.cookie.js" type="text/javascript"></script>
<script src="./js/script.js" type="text/javascript"></script>
<title>dropip console</title>
</head>
<body>

<div class="wrap">

<div id="header">
    <h1>dropip console.</h1>
</div>

<!-- allow ip -->
<div class="tab" id="tab_allowip">
<?= print_config('allowip') ?>
</div>

<!-- allow words -->
<div class="tab" id="tab_allowwords">
<?= print_config('allowwords') ?>
</div>

<!-- deny words -->
<div class="tab" id="tab_denywords">
<?= print_config('denywords') ?>
</div>

<!-- pass.log -->
<div class="tab" id="tab_passlog">
<form method="post" action="">
deny words: <input type="text" name="denywords" /> <input type="submit" value=" insert " />
</form>
<?= print_config('pass.log') ?>
</div>

<!-- exec.log -->
<div class="tab" id="tab_execlog">
<?= print_config('exec.log') ?>
</div>

</div>
</body>
</html>

<?php
exit;

function print_config($filename){
    global $config;

    $array = array();
    $infile = fopen($config['dropip_path'].'/'.$filename, 'r');
    while ($instr = fgets($infile)){
        print $instr."<br />\n";
    }
    fclose($infile);

    return $array;
}

