#!/usr/bin/php
<?php


$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
/*
if (!$result = $mysqli->query($query)) {
    exit;
}
 */

$city = $country = $state = "";


$query= "SELECT * from ops where id > 600000";
$query= "SELECT * from ops where id > 0 and id < 300000";

$query= "SELECT * from ops where id < 100000";
$query= "SELECT * from ops where id > 100000 and id < 300000";
$query= "SELECT * from ops where id > 300000 and id < 500000";
$query= "SELECT * from ops where id > 500000 and id < 700000";
$query= "SELECT * from ops where id > 700000";

$results = $mysqli->query($query);
while ($row = mysqli_fetch_array($results))
{
        $id = $row['id'];
        $ip = $row['ip'];
        $deviceID = trim($row['deviceID']);
        $operation = trim($row['operation']);
        $devicetype = trim($row['devicetype']);
        $filename = trim($row['filename']);
        $seconds = trim($row['seconds']);
        $city = trim($row['city']);
        $country = trim($row['country']);
        $date = trim($row['date']);
        #print("$id $ip $deviceID $operation $devicetype $filename $date");

        $query= "INSERT INTO actions(ip, deviceID, operation, devicetype, filename, date, seconds, city, country) VALUES('$ip', '$deviceID', '$operation', '$devicetype', '$filename', '$date', '$seconds', '$city', '$country')";
        $result = $mysqli->query($query);
}


?>
