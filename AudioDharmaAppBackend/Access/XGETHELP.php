<?php
/*
 * Returns a json file which contains the app help page
 * This entry point  is called directly from the app
 */

$HELP_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/HTML/help00.html";
print(file_get_contents($HELP_PATH));

?>
