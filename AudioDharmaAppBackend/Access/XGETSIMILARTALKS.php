<?php
/*
 * Returns a json file which contains similar talks
 * This entry point is called directly from the app
 */

$SIMILAR_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/SIMILAR/";
$SIMILAR_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/similar/";
$NOFILE = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/SIMILAR/NOFILE";
$MIN_RESULT_SIZE = 300;


function mylog($msg)
{
    $LOGFILE= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Access/ad.log";

    $fp = fopen($LOGFILE, 'a+');
    fputs($fp, "$msg\n");
    fclose($fp);
}

$Key = $_GET["KEY"];
$path = $SIMILAR_PATH . $Key;
mylog($path);
$contents = file_get_contents($path);


// if file not there or not big enough, send back a default
if ($contents == False) {
    $contents = file_get_contents($NOFILE);
    //mylog("returning NOFILE: ", $NOFILE);
}
if (strlen($contents) < $MIN_RESULT_SIZE) {
    $contents = file_get_contents($NOFILE);
    //mylog("returning content too small: ", $NOFILE);
}

// otherwise we have a good result
print($contents);

?>
