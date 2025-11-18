#include <WiFi.h>
#include <WebServer.h>

// --- Configuration ---
const char* ssid = "shameer";         // Replace with your Wi--Fi network name
const char* password = "shameer1985"; // Replace with your Wi-Fi password
const int buzzerPin = 13;                    // The GPIO pin connected to the buzzer
const int irEmitterPin = 14;                 // The GPIO pin connected to the IR emitter

// Status tracking
bool buzzerState = false;
bool irState = false;

// --- Web Server Setup ---
WebServer server(80);

// --- Function Prototypes ---
void handleRoot();
void handleBuzzerOn();
void handleBuzzerOff();
void handleIROn();
void handleIROff();
void handleStatus();
void handleNotFound();

void setup() {
  // --- Serial Monitor Initialization ---
  Serial.begin(115200);
  while (!Serial) { ; } // wait for serial port to connect.

  // --- Pin Setup ---
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // Ensure buzzer is off initially
  pinMode(irEmitterPin, OUTPUT);
  digitalWrite(irEmitterPin, LOW); // Ensure IR emitter is off initially
  
  // Initialize states
  buzzerState = false;
  irState = false;
  
  Serial.println("Pin setup complete - Both outputs initialized to LOW");

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
  server.on("/ir/on", handleIROn);    // Endpoint to turn the IR emitter ON
  server.on("/ir/off", handleIROff);  // Endpoint to turn the IR emitter OFF
  server.on("/status", handleStatus);  // Endpoint to check pin status
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
  buzzerState = true;
  Serial.print("Buzzer ON - Pin 13: HIGH, Pin 14: ");
  Serial.println(irState ? "HIGH" : "LOW");
  server.send(200, "text/plain", "Buzzer turned ON");
  
  // Verify pin state
  delay(10);
  digitalWrite(buzzerPin, HIGH); // Double-check
}

// Handles the "/off" URL to turn the buzzer off
void handleBuzzerOff() {
  digitalWrite(buzzerPin, LOW);
  buzzerState = false;
  Serial.print("Buzzer OFF - Pin 13: LOW, Pin 14: ");
  Serial.println(irState ? "HIGH" : "LOW");
  server.send(200, "text/plain", "Buzzer turned OFF");
  
  // Verify pin state
  delay(10);
  digitalWrite(buzzerPin, LOW); // Double-check
}

// Handles the "/ir/on" URL to turn the IR emitter on
void handleIROn() {
  digitalWrite(irEmitterPin, HIGH);
  irState = true;
  Serial.print("IR Emitter ON - Pin 13: ");
  Serial.print(buzzerState ? "HIGH" : "LOW");
  Serial.println(", Pin 14: HIGH");
  server.send(200, "text/plain", "IR Emitter turned ON");
  
  // Verify pin state
  delay(10);
  digitalWrite(irEmitterPin, HIGH); // Double-check
}

// Handles the "/ir/off" URL to turn the IR emitter off
void handleIROff() {
  digitalWrite(irEmitterPin, LOW);
  irState = false;
  Serial.print("IR Emitter OFF - Pin 13: ");
  Serial.print(buzzerState ? "HIGH" : "LOW");
  Serial.println(", Pin 14: LOW");
  server.send(200, "text/plain", "IR Emitter turned OFF");
  
  // Verify pin state
  delay(10);
  digitalWrite(irEmitterPin, LOW); // Double-check
}

// Handles status check
void handleStatus() {
  String status = "Buzzer: " + String(buzzerState ? "ON" : "OFF");
  status += ", IR: " + String(irState ? "ON" : "OFF");
  status += ", Pin13: " + String(digitalRead(buzzerPin) ? "HIGH" : "LOW");
  status += ", Pin14: " + String(digitalRead(irEmitterPin) ? "HIGH" : "LOW");
  
  Serial.println(status);
  server.send(200, "text/plain", status);
}

// Handles requests to unknown URLs
void handleNotFound() {
  server.send(404, "text/plain", "404: Not found");
}

