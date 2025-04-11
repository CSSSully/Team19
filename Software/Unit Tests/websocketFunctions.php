<?php

function isValidData($data) {
    return !empty($data) && is_string($data);
}

function broadcastToClients($clients, $data) {
    $count = 0;
    foreach ($clients as $c) {
        if (is_resource($c)) {
            fwrite($c, $data);
            $count++;
        }
    }
    return $count;
}
?>
