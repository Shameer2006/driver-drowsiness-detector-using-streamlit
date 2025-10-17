# Driver Drowsiness Detection System with ESP32 and Streamlit

This project is a real-time driver drowsiness detection system that uses a webcam to monitor a driver's eyes. It leverages computer vision with MediaPipe to calculate the Eye Aspect Ratio (EAR) and determine if the driver is drowsy. When drowsiness is detected, the system sends a signal over Wi-Fi to an ESP32 microcontroller, which triggers a buzzer to alert the driver.

The user interface is built with Streamlit, providing real-time video feedback, status updates, and configurable detection parameters.

## Features

- **Real-Time Eye Monitoring**: Captures video from the webcam and analyzes facial landmarks.
- **Drowsiness Detection**: Calculates the Eye Aspect Ratio (EAR) to detect closed eyes over a specific duration.
- **Wireless Alerts**: Sends HTTP requests over a local Wi-Fi network to trigger a physical alarm.
- **Hardware Integration**: Uses an ESP32 microcontroller and a simple two-pin buzzer for the alarm.
- **Interactive UI**: A Streamlit web application allows for easy configuration and monitoring.
- **Adjustable Sensitivity**: Users can fine-tune the EAR threshold and consecutive frame count for personalized accuracy.

## Folder Structure

```
drowsiness_detection/
├── backend.py          # Core computer vision logic for processing frames
├── streamlit_app.py    # The frontend web application
├── esp32_code.ino      # Arduino code for the ESP32 microcontroller
└── README.md           # This file
```

## Setup and Installation

### 1. Python Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required libraries
pip install streamlit opencv-python mediapipe scipy requests av
```

### 2. Hardware

- ESP32 Development Board
- Two-pin buzzer
- Breadboard and jumper wires

**Wiring:**

- Connect the positive leg (+) of the buzzer to a GPIO pin on the ESP32 (e.g., GPIO 13).
- Connect the negative leg (-) of the buzzer to a GND pin on the ESP32.

### 3. ESP32 Setup

1. Open `esp32_code.ino` in the Arduino IDE.
2. Install the required libraries for the ESP32 (e.g., WiFi.h, WebServer.h).
3. Update the following lines with your Wi-Fi network credentials:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

4. Upload the code to your ESP32 board.
5. Open the Serial Monitor (baud rate 115200) to find the IP address assigned to the ESP32.

## How to Run the System

1. Make sure your computer and the ESP32 are connected to the same Wi-Fi network.
2. Navigate to the project directory in your terminal.
3. Run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

4. Open the provided URL in your browser.
5. Enter the ESP32's IP address in the sidebar and check the "Start Detection" box.

## Our Journey: Struggles and Key Learnings

Building this project was a practical exercise in system integration, involving software, hardware, and networking. We encountered several challenges that provided valuable lessons.

### 1. Initial Dependency Issues

**Struggle**: The application failed to start with a `ModuleNotFoundError: No module named 'av'`.

**Resolution**: We discovered that PyAV is a necessary dependency for Streamlit's video processing capabilities.

**Learning**: Always ensure all project dependencies, including indirect ones, are explicitly listed and installed. A requirements.txt file is best practice for larger projects.

### 2. Hardware Compilation Errors

**Struggle**: The initial ESP32 code failed to compile with the error `'BUILTIN_LED' was not declared in this scope`.

**Resolution**: We realized that `BUILTIN_LED` is not a universally defined constant across all ESP32 board definitions. Since the LED was not essential, we removed the related code.

**Learning**: Microcontroller code can be board-specific. Always test with the target hardware in mind and avoid relying on non-standard definitions if not needed.

### 3. Incorrect Computer Vision Logic

**Struggle**: The EAR values were consistently incorrect (often > 1.0), making the drowsiness detection logic fail.

**Resolution**: A deep dive into the backend.py file revealed that we were using an incorrect set of MediaPipe landmarks for the EAR calculation. We corrected the landmark indices to match the standard 6-point formula for EAR.

**Learning**: The success of a computer vision algorithm is highly dependent on the accuracy of the underlying data points. It is crucial to double-check and validate the specific landmark indices or data models being used. Visualizing the data (e.g., drawing landmarks on the frame) is an invaluable debugging tool.

### 4. Critical Networking Failure (The Biggest Hurdle)

**Struggle**: Even with correct code, the buzzer would not trigger. We received a `Request to ESP32 timed out` error, and manual ping commands failed with `Destination host unreachable`.

**Resolution**: This was the most challenging issue. We systematically diagnosed it by:

- Verifying the ESP32's IP address via the Serial Monitor.
- Attempting to ping the device.
- Using a Direct Browser Test (`http://<ESP32_IP>/on`) which also failed.

This process proved that the issue was not in our code but in the network itself. The cause was AP Isolation (or Client Isolation), a security feature on the mobile hotspot that prevents connected devices from communicating with each other. The solution was to switch to a network where this feature was disabled (a home Wi-Fi router or a hotspot created by a laptop).

**Learning**: When integrating networked devices, always assume the network can be a point of failure. A layered debugging approach is essential. Test connectivity at the lowest possible level (like ping or a direct browser request) before debugging the application code. Understanding network security features like AP Isolation is crucial for IoT projects.

This project was a fantastic journey from a simple idea to a fully functional system, teaching us invaluable lessons in debugging across software, hardware, and networking domains.