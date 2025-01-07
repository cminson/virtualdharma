#!/usr/bin/php
<?php

/* 
 * Record into the database that a talk has been played or shared.
 * This access point is called directly by the app.
 */

$MAX_DUPLICATE_WINDOW = 100;
$MAX_DUPLICATE_SHARE = 20;

$ACCESS_KEY_PATH = "/var/www/virtualdharma/KEYS/IPSTACK.KEYS";

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


//
// First, try to get the geolocations from our cache ...
// 
$country = $city = "NA";
$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
$query= "SELECT country,city from ipmap where ip=\"$ip\" LIMIT 1";

//mylog($query);
if (!$result = $mysqli->query($query)) {
    exit;
}

$city = $country = $state = "";

$results = $mysqli->query($query);
while ($row = mysqli_fetch_array($results))
{
    	$country = $row['country'];
    	$city = $row['city'];
        $country = trim($country);
        $city = trim($city);
} 
if ($country != "") {
    mylog("CACHED IP FOUND:  $ip $country $city");
} 

//
// if cache failed, then got to ipstack and use that to geolocate
// and then cache the results for use next time
//
// ipstack.com
// christopherminson@icloud.com ireland
//

$access_key = trim(file_get_contents($ACCESS_KEY_PATH));


if ($country == "") {

    mylog("CACHED IP NOT FOUND:  Doing lookup on $ip");
    $command = "curl https://api.ipstack.com/$ip?access_key=$access_key";

    mylog("Looking up IP: $ip");
    $result = exec("$command 2>&1", $lines, $ConvertResultCode);
    $json = json_decode($result,TRUE);
    mylog("$json");
    $country= $json["country_code"];
    $state = $json["region_code"];
    $city = $json["city"];
    mylog("IPStack Lookup Result: $ip Country: $country City:$city");

    if ($country != "") {
        mylog("STORING IP INTO CACHE: $country $city $ip");
        $query= "INSERT INTO ipmap(ip, country, city) VALUES('$ip', '$country', '$city')";
        mylog($query);
        $result = $mysqli->query($query);
    }
}

$attr1 = $attr2 = $attr3 = "";


$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");

//
// if the SAME talk or share action has been taken by this IP within
// the last MAX_DUPLICATE_WINDOW, filter it out.
//
// This is to prevent runaway reporting by bad clients
//
$shareCount = 0;
$query = "SELECT * FROM actions ORDER by id DESC LIMIT $MAX_DUPLICATE_WINDOW";
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

// legacy insert record
/*
$query= "INSERT INTO ops(ip, deviceID, operation, devicetype, sharetype, filename, date, seconds, city, state,country, zip, latitude, longitude, attr1, attr2, attr3) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$sharetype', '$filename', '$date', '$seconds', '$city', '$state', '$country', '$zip', '$latitude', '$longitude', '$attr1', '$attr2', '$attr3')";
mylog("INSERTING LEGACY RECORD $query");
$result = $mysqli->query($query);
 */

// current insert record
$query= "INSERT INTO actions(ip, deviceID, operation, devicetype, filename, date, seconds, city, country) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$filename', '$date', '$seconds', '$city', '$country')";
//mylog("INSERTING RECORD $query");
//

// 
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
