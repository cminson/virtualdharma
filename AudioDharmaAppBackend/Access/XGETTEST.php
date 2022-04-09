<?php
/* 
 * Returns a json file which contains today's talks and shares activity
 * This entry point is called directly by the app.
 */

$PATH_ACTIVITY_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TEST.JSON";
print(file_get_contents($PATH_ACTIVITY_JSON));

?>
