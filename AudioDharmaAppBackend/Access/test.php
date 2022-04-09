#!/usr/bin/php
<?php

/* 
 * Record into the database that a talk has been played or shared.
 * This access point is called directly by the app.
 */

$MAX_DUPLICATE_WINDOW = 100;
$MAX_DUPLICATE_SHARE = 20;

$deviceID = $operation = $sharetype = $filename = "NA";
$deviceID = $city = $country = $zip = $altitude = $latitude = $longitude = "NA";

$devicetype = getVar("DEVICETYPE");
$deviceID = getVar("DEVICEID");
$operation = getVar("OPERATION");
$sharetype = getVar("SHARETYPE");
$filename = getVar("FILENAME");
$zip = getVar("ZIP");
$altitude = getVar("ALTITUDE");
$latitude = getVar("LATITUDE");
$longitude = getVar("LONGITUDE");

$seconds = time();
$ip = $_SERVER['REMOTE_ADDR'];
$date = gmdate("Y.m.d");

if ($devicetype == "NA") {
    $devicetype = "iphone";
}

if (strlen($devicetype) < 1) {
    $devicetype = "iphone";
}


$country = $city = "NA";
$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
$query= "SELECT country,city from ops where ip=\"$ip\"";

if (!$result = $mysqli->query($query)) {
    exit;
}

$city = $country = $state = "";

$results = $mysqli->query($query);
while ($row = mysqli_fetch_array($results))
{
    	$country = $row['country'];
    	$city = $row['city'];
		if (($country != '') && ($country != "NA")) break;
		if (($city != '') && ($city != "NA")) break;
} 

//
// ipstack.com
// christopherminson@icloud.com ireland
// 

if ($country == "") {

    //curl http://api.ipstack.com/68.185.3.215?access_key=b1f6f872938649344848b999593cf71d
    //$command = "curl freegeoip.net/json/$ip";
    $command = "curl http://api.ipstack.com/$ip?access_key=b1f6f872938649344848b999593cf71d";
    //mylog($command);
    $result = exec("$command 2>&1", $lines, $ConvertResultCode);
    $json = json_decode($result,TRUE);
    $country= $json["country_code"];
    $state = $json["region_code"];
    $city = $json["city"];
}

$attr1 = $attr2 = $attr3 = "";


$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");

// check for recent excess duplicate traffic, exit if any seen
$shareCount = 0;
$query = "SELECT * FROM ops ORDER by id DESC LIMIT $MAX_DUPLICATE_WINDOW";
$result = $mysqli->query($query);
if (mysqli_num_rows($result) > 0) 
{
    while ($row = mysqli_fetch_assoc($result)) 
    {
        $row_ip = $row['ip'];
        $row_filename = $row['filename'];
        $row_operation = $row['operation'];

		// if duplicate plays of talk seen for given ip, exit
        if (($row_ip == $ip) && ($row_filename == $filename) && ($row_operation == 'PLAYTALK'))
        {
            return;
        }

		// if too many shares for a talk seen, exit
        if (($row_ip == $ip) && ($row_filename == $filename) && ($row_operation == 'SHARETALK'))
        {
			$shareCount += 1;
			if ($shareCount > $MAX_DUPLICATE_SHARE) return;
        }
    }
}

// insert the record
$query= "INSERT INTO ops(ip, deviceID, operation, devicetype, sharetype, filename, date, seconds, city, state,country, zip, latitude, longitude, attr1, attr2, attr3) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$sharetype', '$filename', '$date', '$seconds', '$city', '$state', '$country', '$zip', '$latitude', '$longitude', '$attr1', '$attr2', '$attr3')";
$result = $mysqli->query($query);


function mylog($msg) 
{
    $LOGFILE= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Access/ad.log";

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
