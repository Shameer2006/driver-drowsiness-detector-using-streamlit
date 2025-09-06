#include <WiFi.h>
#include <WebServer.h>

// --- Configuration ---
const char* ssid = "shameer";         // Replace with your Wi--Fi network name
const char* password = "shameer1985"; // Replace with your Wi-Fi password
const int buzzerPin = 13;                    // The GPIO pin connected to the buzzer

// --- Web Server Setup ---
WebServer server(80);

// --- Function Prototypes ---
void handleRoot();
void handleBuzzerOn();
void handleBuzzerOff();
void handleNotFound();

void setup() {
  // --- Serial Monitor Initialization ---
  Serial.begin(115200);
  while (!Serial) { ; } // wait for serial port to connect.

  // --- Pin Setup ---
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // Ensure buzzer is off initially

  // --- Wi-Fi Connection ---
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Failed to connect to WiFi. Please check your credentials.");
    // Halt the program if WiFi connection fails.
    while(true) {
      delay(1000); // Infinite loop to stop execution
    }
  }


  // --- Web Server Routes ---
  server.on("/", handleRoot);
  server.on("/on", handleBuzzerOn);   // Endpoint to turn the buzzer ON
  server.on("/off", handleBuzzerOff); // Endpoint to turn the buzzer OFF
  server.onNotFound(handleNotFound);

  // --- Start Server ---
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  // Handle client requests
  server.handleClient();
}

// --- Handler Functions ---

// Handles the root URL ("/")
void handleRoot() {
  server.send(200, "text/plain", "ESP32 Drowsiness Buzzer is online!");
}

// Handles the "/on" URL to turn the buzzer on
void handleBuzzerOn() {
  digitalWrite(buzzerPin, HIGH);
  Serial.println("Buzzer ON");
  server.send(200, "text/plain", "Buzzer turned ON");
}

// Handles the "/off" URL to turn the buzzer off
void handleBuzzerOff() {
  digitalWrite(buzzerPin, LOW);
  Serial.println("Buzzer OFF");
  server.send(200, "text/plain", "Buzzer turned OFF");
}

// Handles requests to unknown URLs
void handleNotFound() {
  server.send(404, "text/plain", "404: Not found");
}

