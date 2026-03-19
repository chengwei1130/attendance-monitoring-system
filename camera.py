import cv2
import time
from deepface import DeepFace
from db import get_all_staff, get_today_record, insert_check_in, update_check_out
import os
import threading

print("Initializing camera module...")

# Global camera instance
camera = None
camera_lock = threading.Lock()

def get_camera():
    """Get or create camera instance with proper locking"""
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            print("[CAMERA] Opening camera...")
            # Try different backends in order of preference
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
                camera = cv2.VideoCapture(0, backend)
                if camera.isOpened():
                    # Set camera properties for better performance
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    camera.set(cv2.CAP_PROP_FPS, 30)
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to get latest frame
                    print(f"[CAMERA] ✓ Camera opened successfully with backend {backend}")
                    break
                else:
                    print(f"[CAMERA] ✗ Failed to open with backend {backend}")
            
            if not camera.isOpened():
                print("[CAMERA] ✗ Failed to open camera with all backends!")
        return camera

def release_camera():
    """Safely release camera resources"""
    global camera
    with camera_lock:
        if camera is not None:
            print("[CAMERA] Releasing camera...")
            camera.release()
            camera = None

# Initialize camera on module load
get_camera()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
last_check_time = 0
CHECK_INTERVAL = 6
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise Exception(f"Haarcascade failed to load from {cascade_path}")

recent_detections = {}
DETECTION_COOLDOWN = 20

TEMP_DIR = os.path.join(BASE_DIR, "temp_frames")
os.makedirs(TEMP_DIR, exist_ok=True)

verification_running = False
status_message = ""
status_color = (0, 255, 0)
status_expire_time = 0
STATUS_DURATION = 4

# ===== ADJUSTABLE THRESHOLDS =====
FACE_SCALE_FACTOR = 1.3
FACE_MIN_NEIGHBORS = 6
FACE_MIN_SIZE = (80, 80)
VERIFICATION_THRESHOLD = 0.4
# ==================================
def set_status_message(message, color=(0, 255, 0), duration=4):
    """Set temporary status message to show on camera feed"""
    global status_message, status_color, status_expire_time
    status_message = message
    status_color = color
    status_expire_time = time.time() + duration
    
def verify_face_async(frame, staff_list):
    """Run face verification in background thread"""
    global verification_running, recent_detections
    try:
        verification_running = True
        temp_frame_path = os.path.join(TEMP_DIR, "current_frame.jpg")
        cv2.imwrite(temp_frame_path, frame)
        
        current_time = time.time()
        
        # Clean up old detections
        recent_detections = {k: v for k, v in recent_detections.items() 
                        if current_time - v < DETECTION_COOLDOWN}
        
        print(f"[VERIFY] Checking {len(staff_list)} staff members...")
        
        for staff_id, name, photo_path in staff_list:
            try:
                if staff_id in recent_detections:
                    print(f"[SKIP] {name} - Recently detected (cooldown: {DETECTION_COOLDOWN}s)")
                    continue

                if not os.path.exists(photo_path):
                    print(f"[ERROR] Photo not found for {name}: {photo_path}")
                    continue

                print(f"[VERIFY] Comparing with {name}...")
                
                result = DeepFace.verify(
                    img1_path=temp_frame_path,
                    img2_path=photo_path,
                    enforce_detection=True,
                    detector_backend='opencv',
                    model_name='Facenet',
                    distance_metric='cosine'
                )

                distance = result.get("distance", 1.0)
                verified = result["verified"]
                
                print(f"[RESULT] {name}: verified={verified}, distance={distance:.4f}")

                if verified and distance < VERIFICATION_THRESHOLD:
                    print(f"[MATCH] Face matched for {name} (staff_id: {staff_id})")
                    
                    existing_record = get_today_record(staff_id)
                    
                    if existing_record is None:
                        print(f"[CHECK-IN] No record found, checking in {name}...")
                        try:
                            insert_check_in(staff_id)
                            recent_detections[staff_id] = current_time
                            set_status_message(f"{name} [{staff_id}] Attendance is recorded", (0, 255, 0), STATUS_DURATION)
                            print(f"✓✓✓ CHECK-IN SUCCESS: {name} has checked in! ✓✓✓")

                        except Exception as save_error:
                            print(f"[ERROR] Failed to check in: {save_error}")
                    else:
                        print(f"[CHECK-OUT] Record found (ID: {existing_record[0]}), checking out {name}...")
                        try:
                            update_check_out(staff_id)
                            recent_detections[staff_id] = current_time
                            set_status_message(f"{name} [{staff_id}] Attendance is recorded", (0, 255, 0), STATUS_DURATION)
                            print(f"✓✓✓ CHECK-OUT SUCCESS: {name} has checked out! ✓✓✓")

                        except Exception as save_error:
                            print(f"[ERROR] Failed to check out: {save_error}")
                    
                    break
                else:
                    print(f"[REJECT] {name} - Not matched (distance: {distance:.4f}, threshold: {VERIFICATION_THRESHOLD})")

            except Exception as e:
                error_msg = str(e)
                if "Face could not be detected" in error_msg:
                    print(f"[INFO] No clear face detected in photo for {name}")
                else:
                    print(f"[ERROR] Exception for {name}: {error_msg}")
                    
    except Exception as e:
        print(f"[ERROR] verify_face_async failed: {e}")
        set_status_message("Verification failed", (0, 0, 255), 3)
    finally:
        verification_running = False
        print("[VERIFY] Verification complete\n")

def generate_frame():
    """Generate video frames for streaming"""
    global last_check_time
    
    print("[STREAM] generate_frame() called - Stream starting")
    staff_list = get_all_staff()
    print(f"[STREAM] Staff list loaded: {len(staff_list)} staff members")
    
    if len(staff_list) == 0:
        print("[WARNING] No staff registered in database!")
    
    frame_count = 0
    consecutive_failures = 0
    MAX_FAILURES = 10

    try:
        while True:
            cam = get_camera()
            
            # Double-check camera is opened
            if not cam or not cam.isOpened():
                print("[ERROR] Camera not opened, attempting to reconnect...")
                consecutive_failures += 1
                if consecutive_failures >= MAX_FAILURES:
                    print("[FATAL] Too many consecutive failures, stopping stream")
                    break
                time.sleep(0.5)
                get_camera()  # Try to reopen
                continue
            
            success, frame = cam.read()

            if not success or frame is None:
                consecutive_failures += 1
                print(f"[WARNING] Frame read failed (attempt {consecutive_failures}/{MAX_FAILURES})")
                
                if consecutive_failures >= MAX_FAILURES:
                    print("[ERROR] Too many consecutive frame read failures")
                    release_camera()  # Release and try fresh connection
                    time.sleep(1)
                    get_camera()
                    consecutive_failures = 0
                
                time.sleep(0.1)
                continue
            
            # Reset failure counter on success
            consecutive_failures = 0
            frame_count += 1
            
            if frame_count % 60 == 0:  # Print every 60 frames (every 2 seconds)
                print(f"[STREAM] ✓ Frames: {frame_count}")

            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            current_time = time.time()
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            try:
                faces = face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=FACE_SCALE_FACTOR,
                    minNeighbors=FACE_MIN_NEIGHBORS,
                    minSize=FACE_MIN_SIZE
                )
            except Exception as e:
                print(f"[ERROR] Face detection error: {e}")
                faces = []

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Start verification in background if conditions met
            if (current_time - last_check_time > CHECK_INTERVAL and 
                len(faces) > 0 and 
                not verification_running):
                
                print(f"\n{'='*50}")
                print(f"[TRIGGER] Starting verification for {len(faces)} detected face(s)")
                print(f"{'='*50}")
                last_check_time = current_time
                thread = threading.Thread(target=verify_face_async, args=(frame.copy(), staff_list))
                thread.daemon = True
                thread.start()
                
            if time.time() < status_expire_time and status_message:
                cv2.rectangle(frame, (20, 20), (620, 70), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, 20), (620, 70), status_color, 2)
                cv2.putText(
                    frame,
                    status_message,
                    (30, 52),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    status_color,
                    2,
                    cv2.LINE_AA
                )

            # Encode frame to JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                print(f"[ERROR] Failed to encode frame {frame_count}")
                continue
            
            # Convert to bytes and yield
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    except GeneratorExit:
        print("[STREAM] Client disconnected from video stream")
    except Exception as e:
        print(f"[ERROR] Exception in generate_frame: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[STREAM] Stream ended")

def get_single_frame():
    """Get a single frame from camera"""
    cam = get_camera()
    
    if not cam or not cam.isOpened():
        print("[ERROR] get_single_frame: Camera not opened")
        return None
    
    success, frame = cam.read()

    if not success or frame is None:
        print("[ERROR] get_single_frame: Failed to read frame")
        return None
    
    frame = cv2.flip(frame, 1)
    return frame