<?php
include('websocketFunctions.php');

// === Simple Unit Test Functions ===
function assertEquals($input, $expectedOutput) {
    if ($input == $expectedOutput) {
        echo "✅ SUCCESS<br>";
        return true;
    } else {
        echo "❌ FAILED - Expected " . var_export($expectedOutput, true) . ", got " . var_export($input, true) . "<br>";
        return false;
    }
}

function assertTrue($input) {
    return assertEquals($input, true);
}

function assertFalse($input) {
    return assertEquals($input, false);
}

// === Unit Tests ===
echo "<h2>WebSocket Utility Function Tests</h2>";

echo "<h3>Test isValidData()</h3>";
assertTrue(isValidData("sensor_001: 42"));
assertFalse(isValidData(""));
assertFalse(isValidData(null));

echo "<h3>Test broadcastToClients()</h3>";

// Create test clients (memory streams for simulation)
$client1 = fopen('php://memory', 'w+');
$client2 = fopen('php://memory', 'w+');
$clients = [$client1, $client2];

$data = "test_data";
$count = broadcastToClients($clients, $data);
assertEquals($count, 2);

// Close mock clients
fclose($client1);
fclose($client2);
?>
