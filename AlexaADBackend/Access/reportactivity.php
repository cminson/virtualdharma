<?php


$deviceID = $operation = $sharetype = $filename = "NA";
$deviceID = $zip = $altitude = $latitude = $longitude = "NA";
$ip = "NA";

$devicetype = "alexa";

$deviceID = getVar("USERID");
$operation = "PLAYTALK";
$filename = getVar("FILENAME");

$city = "Alexa Cloud";
$state = "";
$country = "";

$seconds = time();
$date = gmdate("Y.m.d");


$attr1 = $attr2 = $attr3 = "";

$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
//$query= "INSERT INTO ops(ip, deviceID, operation, devicetype, sharetype, filename, date, seconds, city, state,country, zip, latitude, longitude, attr1, attr2, attr3) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$sharetype', '$filename', '$date', '$seconds', '$city', '$state', '$country', '$zip', '$latitude', '$longitude', '$attr1', '$attr2', '$attr3')";
//$result = $mysqli->query($query);
$query= "INSERT INTO actions(ip, deviceID, operation, devicetype, filename, date, seconds, city, country) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$filename', '$date', '$seconds', '$city', '$country')";
$result = $mysqli->query($query);
//mylog($query);

function mylog($msg)
{
    $LOGFILE= "/var/www/virtualdharma/httpdocs/AlexaADBackend/Access/ad.log";

    $fp = fopen($LOGFILE, 'a+');
    fputs($fp, "$msg\n");
    fclose($fp);
}


function getVar($var) 
{
    if (isset($_POST[$var]))
    {
        return $_POST[$var];
    }
    if (isset($_GET[$var]))
    {
        return $_GET[$var];
    }
    return "";
}
?>

