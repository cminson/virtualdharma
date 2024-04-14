<?php
/*
 * Returns a response from the server for a query
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

// Construct the GET parameters
$get_params = http_build_query(array('ARG_COMMAND' => $command, 'ARG_QUERY' => $query));

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

// Construct the HTTP request
$http_request = "GET /?" . $get_params . " HTTP/1.1\r\n";
$http_request .= "Host: localhost:3022\r\n";
$http_request .= "Connection: close\r\n\r\n";

// Send the HTTP request to the local program
socket_write($socket, $http_request, strlen($http_request));

// Receive the response from the local program
$response = '';
while ($out = socket_read($socket, $MAX_RESPONSE_SIZE)) {
    $response .= $out;
}

// Close the socket
socket_close($socket);

// Print the response
echo $response;
?>

