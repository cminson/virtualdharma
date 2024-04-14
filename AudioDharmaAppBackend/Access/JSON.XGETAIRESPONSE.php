<?php
/*
 * Returns a json file which contains AI response for a query
 * This entry point is called directly from the app
 */

function mylog($msg)
{
    $LOGFILE= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Access/ad.log";

    $fp = fopen($LOGFILE, 'a+');
    fputs($fp, "$msg\n");
    fclose($fp);
}

$SOPHIA_PORT = 3022;
$MAX_RESPONSE_SIZE = 10000;

// Get the QUERY and COMMAND arguments from the CGI request
$query = isset($_GET['QUERY']) ? $_GET['QUERY'] : '';
$command = isset($_GET['COMMAND']) ? $_GET['COMMAND'] : '';

$command = "GET_EXPLORE";
$query = "love";

// Make sure QUERY and COMMAND are not empty
if (empty($query) || empty($command)) {
    echo "QUERY and COMMAND parameters are required.";
    exit(1);
}

// Create a JSON payload with QUERY and COMMAND
$data = json_encode(array('QUERY' => $query, 'COMMAND' => $command));

// Create a TCP/IP socket
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "socket_create() failed: " . socket_strerror(socket_last_error());
    exit(1);
}

// Connect to the local program listening on port 3022
$result = socket_connect($socket, 'localhost', 3022);
if ($result === false) {
    echo "socket_connect() failed: " . socket_strerror(socket_last_error());
    exit(1);
}

print("connected\n");

// Send the data to the local program
socket_write($socket, $data, strlen($data));

print("written\n");

// Receive the response from the local program
$response = '';
while ($out = socket_read($socket, 10000)) {
    $response .= $out;
}
print("response seen\n");

// Close the socket
socket_close($socket);

// Print the response
echo $response;
?>

?>
