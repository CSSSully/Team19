<?php
$host = '0.0.0.0'; // Listen on all interfaces
$port = 8080;

$server = stream_socket_server("tcp://$host:$port", $errno, $errstr);
if (!$server) {
    die("WebSocket server failed: $errstr ($errno)");
}

$clients = [];

while (true) {
    $read = $clients;
    $read[] = $server;
    $write = $except = null;

    if (stream_select($read, $write, $except, 0, 200000)) {
        if (in_array($server, $read)) {
            $client = stream_socket_accept($server);
            $clients[] = $client;
            unset($read[array_search($server, $read)]);
        }

        foreach ($read as $client) {
            $data = fread($client, 1024);
            if (!$data) {
                fclose($client);
                unset($clients[array_search($client, $clients)]);
                continue;
            }

            // Broadcast the sensor data to all connected clients
            foreach ($clients as $c) {
                fwrite($c, $data);
            }
        }
    }
}

fclose($server);
?>
