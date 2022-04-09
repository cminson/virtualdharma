<?php


$TEST1 = $_POST["TEST1"];
//print("https://audiodharma.org//teacher/78/talk/8050/venue/IMC/20170719-Berget_Jelane-IMC-practice_notes_emotions.mp3");
//print("https://s3.amazonaws.com/virtualdharma.org/20170917-Gil_Fronsdal-IMC-on_the_way_to_unshakeable_faith.mp3")
print("https://s3.amazonaws.com/virtualdharma.org/test01.mp3")


$MAX_READS = 3;
//$ACTIVITY_FILE = "/test.json";
$ACTIVITY_FILE = "/activity.json";

$res = "";
$cwd = getcwd();
$file = "$cwd$ACTIVITY_FILE";
//print($file);
for ($i = 0; $i < $MAX_READS; $i++)
{

    $res = file_get_contents($file);
    if (strlen($res) > 10)
        break;
    sleep(1);
}
print $res;


?>
