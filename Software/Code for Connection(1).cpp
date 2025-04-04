#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "YOUR_WIfi_you_using";
const char* password = "YOUR_WIFI_PASSWORD_you_are_consuming";
WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch (type) {
        case WStype_DISCONNECTED:
            Serial.println("Disconnected!");
            break;
        case WStype_CONNECTED:
            Serial.println("Connected!");
            break;
        case WStype_TEXT:
            Serial.printf("Received: %s\n", payload);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting...");
    }ø

    Serial.println("Connected to WiFi");

    webSocket.begin("YOUR_SERVER_IP", 8080, "/");
    webSocket.onEvent(webSocketEvent);
}

void loop() {
    int sensorData = analogRead(34); // Example: Read from a sensor
    String message = "Temperature Value: " + String(sensorData);

    webSocket.sendTXT(message);
    webSocket.loop();
    
    delay(30000);
}
