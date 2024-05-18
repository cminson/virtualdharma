<?php
/*
 * Returns a response from the server for a query
 * This entry point is called directly from the app
 */

function LOGGING($msg)
{
    $LOGFILE= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/LOGS/AD.LOG";

    $fp = fopen($LOGFILE, 'a+');
    fputs($fp, "ACCESS XGETAIRESPONSE.php: $msg\n");
    fclose($fp);
}

$start_time = microtime(true);

$SOPHIA_PORT = 3000;
$MAX_RESPONSE_SIZE = 10000;

// Get the QUERY and COMMAND arguments from the CGI request
$query = $_GET["QUERY"];
//$query = "Love";
LOGGING("QUERY: $query");
$command = "GET_EXPLORE";

// Make sure QUERY and COMMAND are not empty
/*
if (empty($query) || empty($command)) {
    echo "QUERY and COMMAND parameters are required.";
    exit(1);
}
 */

// Construct the GET parameters
$get_params = http_build_query(array('ARG_COMMAND' => $command, 'ARG_QUERY' => $query));

// Create a TCP/IP socket
$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "socket_create() failed: " . socket_strerror(socket_last_error());
    exit(1);
}

// Connect to the local program listening on port 
$result = socket_connect($socket, 'localhost', $SOPHIA_PORT);
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

$end_time = microtime(true);
$elapsed_time = ($end_time - $start_time) * 1000;
LOGGING("Query Complete");
LOGGING($response);
LOGGING("Elapsed Time: $elapsed_time");

echo $response;
?>

