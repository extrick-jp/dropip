<?php
/*
    console.php
    for dropip
-------------------------------------------------------------------------------*/
ini_set('display_errors', 'On');

$config = array(
    'dropip_path' => '/usr/local/bin/dropip',
);

require_once 'sub_print.php';
print_header(
    'dropip console',
);
?>

<!-- allow ip -->
<!-- allow words -->
<!-- deny words -->

<form method="post">
</form>

<!-- error count -->

<?php
print_footer();
exit;

function get_array_allowip(){
    global $config;

    $array = array();
    $infile = fopen($config['dropip_path'].'/allowip', 'r');
    while ($instr = fgets($infile)){
        $instr = str_replace('//', '/', $instr);
        list($ip, $comment) = explode('/', $instr);
        $ip = trim($ip);
    }
    fclose($infile);

    return $array;
}
