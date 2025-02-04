<?php
/*
 * Returns a json file which contains similar talks
 * This entry point is called directly from the app
 */

$PATH_TRANSCRIPT = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/transcripts/";
$PATH_SUMMARY = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/summaries/";


$Data = [
    "summaryLong" => "Summary available soon.",
    "transcriptText" => "Transcript available soon."
];


function LOGGING($msg)
{
       $LOGFILE= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/LOGS/AD.LOG";
 
      $fp = fopen($LOGFILE, 'a+');
      fputs($fp, "ACCESS XGETTRANSCRIPT.php: $msg\n");
      fclose($fp);
}


$json = json_encode($Data);

$Key = $_GET["KEY"];
LOGGING($Key);
//$Key = "Gil_101205_Refuges_Wk4Pt2.mp3";

$fileName = "transcript." .str_replace(".mp3", ".txt", $Key);
$pathTranscript = $PATH_TRANSCRIPT . $fileName;
$fileName = "talk." . str_replace(".mp3", ".long", $Key);
$pathSummary = $PATH_SUMMARY . $fileName;

//print("$pathTranscript\n");
//print("$pathSummary\n");

$transcript = file_get_contents($pathTranscript);
$summaryLong = file_get_contents($pathSummary);


// if file not there or not big enough, send back a default
if ($transcript != false) {

    $Data["transcriptText"] = $transcript;
}
if ($summaryLong != false) {
    $Data["summaryLong"] = $summaryLong;
}


$json = json_encode($Data);
print($json)

?>
