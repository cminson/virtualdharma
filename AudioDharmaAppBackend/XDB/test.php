#!/usr/bin/php
<?php


$city = "Ashland";
$country = "US";
$mysqli = new mysqli("localhost", "cminson", "ireland", "ad");
$query= "SELECT ip from ipmap where city='$city' and country='$country' LIMIT 1";
print($query);
if (!$result = $mysqli->query($query)) {
    exit;
}
while ($row = mysqli_fetch_array($result))
{
    	$ip = $row['ip'];
    	#$country = $row['country'];
    	#$city = $row['city'];
        print($ip);
} 




?>
