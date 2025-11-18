import cv2
import mediapipe as mp
from scipy.spatial import distance as dist
import requests
import socket

# MediaPipe Face Mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Corrected Landmark Indices for EAR Calculation ---
# These are the 6 specific landmarks for the EAR formula (P1, P2, P3, P4, P5, P6)
# Standard EAR formula: EAR = (|P2-P6| + |P3-P5|) / (2 * |P1-P4|)
# Using the most accurate MediaPipe Face Mesh landmarks for eye corners and eyelids
LEFT_EYE_EAR_INDICES = [362, 385, 387, 263, 373, 380]   # [outer_corner, upper1, upper2, inner_corner, lower2, lower1]
RIGHT_EYE_EAR_INDICES = [33, 160, 158, 133, 153, 144]    # [outer_corner, upper1, upper2, inner_corner, lower2, lower1]

# Eye landmarks for drawing the contour (optional, but good for visualization)
LEFT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]


def calculate_ear(eye_landmarks):
    """
    Calculates the Eye Aspect Ratio (EAR) for a single eye using 6 landmarks.
    The EAR is the ratio of the distances between the vertical eye landmarks
    and the distances between the horizontal eye landmarks.
    """
    # The landmarks are expected in the order [P1, P2, P3, P4, P5, P6]
    # Vertical distances
    v1 = dist.euclidean(eye_landmarks[1], eye_landmarks[5]) # P2-P6
    v2 = dist.euclidean(eye_landmarks[2], eye_landmarks[4]) # P3-P5

    # Horizontal distance
    h = dist.euclidean(eye_landmarks[0], eye_landmarks[3]) # P1-P4

    # Compute the eye aspect ratio, avoid division by zero
    if h == 0:
        return 0.0
    ear = (v1 + v2) / (2.0 * h)
    return ear

def process_frame(frame, frame_counter, drowsy_status, eye_ar_thresh, eye_ar_consec_frames):
    """
    Processes a single video frame to detect drowsiness.
    Now accepts thresholds as arguments.
    """
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    ear = 0.0 # Initialize EAR

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            h, w, _ = frame.shape

            # --- Use the corrected 6 landmarks for EAR calculation ---
            left_ear_coords = [(landmarks[i].x, landmarks[i].y) for i in LEFT_EYE_EAR_INDICES]
            right_ear_coords = [(landmarks[i].x, landmarks[i].y) for i in RIGHT_EYE_EAR_INDICES]
            
            left_ear = calculate_ear(left_ear_coords)
            right_ear = calculate_ear(right_ear_coords)
            ear = (left_ear + right_ear) / 2.0

            # --- Use the full contour for drawing ---
            left_eye_contour = [(landmarks[i].x * w, landmarks[i].y * h) for i in LEFT_EYE_LANDMARKS]
            right_eye_contour = [(landmarks[i].x * w, landmarks[i].y * h) for i in RIGHT_EYE_LANDMARKS]
            for point in left_eye_contour + right_eye_contour:
                cv2.circle(frame, (int(point[0]), int(point[1])), 1, (0, 255, 0), -1)


            # Check for drowsiness using passed thresholds
            if ear < eye_ar_thresh:
                frame_counter += 1
                if frame_counter >= eye_ar_consec_frames:
                    drowsy_status = True
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                frame_counter = 0
                drowsy_status = False
    
    # Display the calculated EAR on the frame
    cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return frame, frame_counter, drowsy_status, ear

def test_esp32_connection(esp32_ip):
    """
    Test ESP32 connectivity with multiple methods
    """
    print(f"Testing connection to ESP32 at {esp32_ip}...")
    
    # Test 1: Ping test
    import subprocess
    try:
        result = subprocess.run(['ping', '-n', '1', esp32_ip], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ Ping successful")
        else:
            print("✗ Ping failed")
    except:
        print("✗ Ping test failed")
    
    # Test 2: Socket test
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        result = sock.connect_ex((esp32_ip, 80))
        sock.close()
        if result == 0:
            print("✓ Port 80 reachable")
            return True
        else:
            print("✗ Port 80 not reachable")
            return False
    except Exception as e:
        print(f"✗ Socket test failed: {e}")
        return False

def send_signal_to_esp32(esp32_ip, status):
    """
    Sends a signal to the ESP32 to turn the buzzer on or off.
    Returns a tuple (success_boolean, status_message).
    """
    action = 'on' if status else 'off'
    url = f"http://{esp32_ip}/{action}"
    
    # Longer timeout for OFF signals
    timeout = 8.0 if not status else 5.0
    
    print(f"Attempting {action.upper()} to {url} (timeout: {timeout}s)")
    
    try:
        # Quick connectivity check
        if not test_esp32_connection(esp32_ip):
            message = f"ESP32 at {esp32_ip} not reachable - Check IP/WiFi"
            return False, message
        
        # Send HTTP request
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            message = f"Buzzer {action.upper()} successful"
            print(f"ESP32 Response: {response.text}")
            return True, message
        else:
            message = f"ESP32 error: Status {response.status_code}"
            print(f"Response: {response.text}")
            return False, message
            
    except socket.timeout:
        message = "Socket timeout - ESP32 not responding on port 80"
        print(message)
        return False, message
    except requests.exceptions.Timeout:
        message = f"HTTP timeout after {timeout}s - ESP32 overloaded"
        print(message)
        return False, message
    except Exception as e:
        message = f"Connection error: {str(e)[:80]}"
        print(message)
        return False, message

