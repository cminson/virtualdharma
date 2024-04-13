#!/usr/bin/php
<?php


$IPArray = array();
$country = $city = "NA";
$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
$query= "SELECT ip,country,city from ops";
if (!$result = $mysqli->query($query)) {
    exit;
}
while ($row = mysqli_fetch_array($result))
{
    	$ip = $row['ip'];
    	$country = $row['country'];
    	$city = $row['city'];
        $IPDict[$ip] = "$country, $city";
} 

foreach ($IPDict as $ip => $location) {

    list($country, $city) = explode(",", $location);
    $country = trim($country);
    $city = trim($city);
    #print("$ip $country $city\n");
    $query= "INSERT INTO ipmap(ip, country, city) VALUES('$ip', '$country', '$city')";
    $result = $mysqli->query($query);
}

//print("$ip $country $city\n");
//$result = $mysqli->query($query);



?>
