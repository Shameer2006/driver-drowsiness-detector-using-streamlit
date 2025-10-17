import streamlit as st
import cv2
from backend import process_frame, send_signal_to_esp32
import time

# --- Streamlit Web App Configuration ---
st.set_page_config(page_title="Drowsiness Detection", layout="wide")
st.title("Driver Drowsiness Detection System")
st.write("This application uses your webcam to monitor your eyes and detect signs of drowsiness. If your eyes remain closed for an extended period, an alert will be triggered on the ESP32.")

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")
    run_detection = st.checkbox("Start Detection", value=False)
    
    st.subheader("Detection Parameters")
    # Add sliders for real-time adjustment
    ear_thresh = st.slider("Eye Aspect Ratio (EAR) Threshold", 0.1, 0.4, 0.23, 0.01)
    consec_frames = st.slider("Consecutive Frames Threshold", 5, 50, 15, 1)
    
    st.info("Adjust the sliders to calibrate the detection sensitivity. A lower EAR threshold requires the eyes to be more closed to trigger an alert.")

    st.header("ESP32 Communication")
    esp32_ip = st.text_input("ESP32 IP Address", "192.168.1.10")
    
    col1_btn, col2_btn = st.columns(2)
    with col1_btn:
        if st.button("Test Buzzer ON"):
            success, message = send_signal_to_esp32(esp32_ip, True)
            if success:
                st.success(message)
            else:
                st.error(message)
            time.sleep(1) # Give feedback time to be seen

    with col2_btn:
        if st.button("Test Buzzer OFF"):
            success, message = send_signal_to_esp32(esp32_ip, False)
            if success:
                st.success(message)
            else:
                st.error(message)


# --- Main Application Area ---
col1, col2 = st.columns([3, 1])
with col1:
    FRAME_WINDOW = st.image([])
with col2:
    status_text = st.empty()
    ear_metric = st.empty()
    esp_status_placeholder = st.empty()


# Initialize session state variables
if 'frame_counter' not in st.session_state:
    st.session_state.frame_counter = 0
if 'drowsy' not in st.session_state:
    st.session_state.drowsy = False
if 'last_signal' not in st.session_state:
    st.session_state.last_signal = False # Tracks the last signal sent to avoid spamming

# --- Video Capture and Processing Logic ---
cap = cv2.VideoCapture(0)

while run_detection and cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.warning("Could not read frame from webcam. Please check your camera connection.")
        break

    # Process the frame for drowsiness, passing the new slider values
    processed_frame, st.session_state.frame_counter, new_drowsy_status, current_ear = process_frame(
        frame,
        st.session_state.frame_counter,
        st.session_state.drowsy,
        ear_thresh,
        consec_frames
    )

    # Update UI
    FRAME_WINDOW.image(processed_frame, channels="BGR")
    ear_metric.metric("Current EAR", f"{current_ear:.2f}")

    if new_drowsy_status:
        status_text.error("Status: Drowsy Detected!")
    else:
        status_text.success("Status: Awake")

    # Send signal to ESP32 only when the status changes
    if new_drowsy_status != st.session_state.last_signal:
        success, message = send_signal_to_esp32(esp32_ip, new_drowsy_status)
        if success:
            esp_status_placeholder.success(message, icon="📶")
        else:
            esp_status_placeholder.error(message, icon="📵")
        st.session_state.last_signal = new_drowsy_status

    st.session_state.drowsy = new_drowsy_status

else:
    if run_detection:
        st.error("Webcam not available.")
    else:
        st.info("Detection is stopped. Check the 'Start Detection' box to begin.")
    
    # Ensure buzzer is off when detection stops
    if st.session_state.get('last_signal', False):
         success, message = send_signal_to_esp32(esp32_ip, False)
         if success:
            esp_status_placeholder.info("Detection stopped. Buzzer turned OFF.", icon="✅")
         else:
            esp_status_placeholder.warning("Detection stopped, but failed to turn buzzer OFF.", icon="⚠️")
         st.session_state.last_signal = False


cap.release()

