import cv2
import time
import threading
import os
import argparse
import subprocess
import json
import numpy as np
import mediapipe as mp
import pyttsx3
from collections import deque
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

# Try to import tensorflow.keras
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except Exception as e:
    print("TensorFlow not available:", e)
    TENSORFLOW_AVAILABLE = False

# ---------------------
# Config
# ---------------------
MODEL_PATH = "fall_detection_model.h5"   # your uploaded .h5
ALARM_FILE = "alarm.wav"                 # provide alarm.wav in same folder
POPUP_SCRIPT = "popup_alert.vbs"         # modal popup helper (optional)
FPS_TARGET = 10                          # process at 10 FPS
PRED_BUFFER = 6                          # buffer length of soft decisions
FALL_PROB_THRESHOLD = 0.55               # model probability threshold for class 'fall'
SUSTAIN_REQUIRED = 3                     # require sustained positive predictions to confirm
LOG_FILE = "fall_log.txt"

class AdvancedFallDetectionSystem:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Initialize model if available
        self.model = None
        if TENSORFLOW_AVAILABLE and os.path.exists(MODEL_PATH):
            try:
                print("Loading model:", MODEL_PATH)
                self.model = load_model(MODEL_PATH, compile=False)
                print("Model loaded. Input shape:", self.model.input_shape, "Output shape:", self.model.output_shape)
            except Exception as e:
                print("Failed to load model:", e)
                self.model = None
        
        # Fall detection parameters
        self.pred_buf = deque(maxlen=PRED_BUFFER)
        self.sustain = 0
        self.last_alert_time = 0
        self.fall_detected = False
        self.alert_active = False
        
        # Health data simulation
        self.heart_rate = 75
        self.previous_falls = 0
        self.current_time = datetime.now()
        
        # Voice system
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 140)
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the dark-themed UI"""
        self.root = tk.Tk()
        self.root.title("Advanced AI Fall Detection System - AITHON 3.0")
        self.root.configure(bg='#1a1a1a')
        self.root.geometry("1400x900")
        
        # Configure dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='#ffffff')
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TButton', background='#333333', foreground='#ffffff')
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Camera feed
        left_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Camera feed label
        self.camera_label = ttk.Label(left_panel, text="📹 Live Camera Feed with AI Detection", style='Dark.TLabel', font=('Arial', 16, 'bold'))
        self.camera_label.pack(pady=(0, 10))
        
        # Video display
        self.video_frame = tk.Frame(left_panel, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status display
        self.status_label = ttk.Label(left_panel, text="✅ Status: Normal", style='Dark.TLabel', font=('Arial', 14, 'bold'))
        self.status_label.pack(pady=10)
        
        # AI Model status
        model_status = "✅ AI Model Loaded" if self.model else "⚠️ AI Model Not Available"
        self.model_status = ttk.Label(left_panel, text=model_status, style='Dark.TLabel', font=('Arial', 12))
        self.model_status.pack(pady=5)
        
        # Right panel - Health data
        right_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Heart rate monitor
        hr_frame = ttk.LabelFrame(right_panel, text="💓 Heart Rate Monitor", style='Dark.TFrame')
        hr_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hr_label = ttk.Label(hr_frame, text=f"{self.heart_rate} BPM", style='Dark.TLabel', font=('Arial', 28, 'bold'))
        self.hr_label.pack(pady=20)
        
        # Previous data
        data_frame = ttk.LabelFrame(right_panel, text="📊 Health Data", style='Dark.TFrame')
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.falls_label = ttk.Label(data_frame, text=f"Previous Falls: {self.previous_falls}", style='Dark.TLabel', font=('Arial', 12))
        self.falls_label.pack(pady=5)
        
        self.time_label = ttk.Label(data_frame, text=f"Time: {self.current_time.strftime('%H:%M:%S')}", style='Dark.TLabel', font=('Arial', 12))
        self.time_label.pack(pady=5)
        
        # AI Detection Info
        ai_frame = ttk.LabelFrame(right_panel, text="🤖 AI Detection Info", style='Dark.TFrame')
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fall_prob_label = ttk.Label(ai_frame, text="Fall Probability: 0.00", style='Dark.TLabel', font=('Arial', 12))
        self.fall_prob_label.pack(pady=5)
        
        self.fps_label = ttk.Label(ai_frame, text="FPS: 0", style='Dark.TLabel', font=('Arial', 12))
        self.fps_label.pack(pady=5)
        
        # Alert controls
        alert_frame = ttk.LabelFrame(right_panel, text="🚨 Alert Controls", style='Dark.TFrame')
        alert_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cancel_button = ttk.Button(alert_frame, text="Cancel False Alarm", command=self.cancel_alert, style='Dark.TButton')
        self.cancel_button.pack(pady=10)
        
        # Voice interaction
        voice_frame = ttk.LabelFrame(right_panel, text="🎤 Voice Interaction", style='Dark.TFrame')
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.voice_status = ttk.Label(voice_frame, text="Voice: Ready", style='Dark.TLabel', font=('Arial', 12))
        self.voice_status.pack(pady=5)
        
        # Test buttons
        test_frame = ttk.LabelFrame(right_panel, text="🧪 Test Controls", style='Dark.TFrame')
        test_frame.pack(fill=tk.X)
        
        ttk.Button(test_frame, text="Simulate Fall", command=self.simulate_fall, style='Dark.TButton').pack(pady=5)
        ttk.Button(test_frame, text="Reset System", command=self.reset_system, style='Dark.TButton').pack(pady=5)
        
    def landmarks_bbox(self, landmarks, frame_w, frame_h, pad=0.25):
        """Compute bounding box from landmarks"""
        xs = [l.x for l in landmarks]
        ys = [l.y for l in landmarks]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        w = max_x - min_x
        h = max_y - min_y
        cx = (max_x + min_x) / 2.0
        cy = (max_y + min_y) / 2.0
        
        w *= (1.0 + pad)
        h *= (1.0 + pad)
        
        x1 = int(max(0, (cx - w/2.0) * frame_w))
        y1 = int(max(0, (cy - h/2.0) * frame_h))
        x2 = int(min(frame_w - 1, (cx + w/2.0) * frame_w))
        y2 = int(min(frame_h - 1, (cy + h/2.0) * frame_h))
        
        if x2 - x1 < 10 or y2 - y1 < 10:
            return 0, 0, frame_w - 1, frame_h - 1
        return x1, y1, x2, y2

    def preprocess_crop_for_model(self, frame, bbox):
        """Preprocess crop for model input"""
        x1, y1, x2, y2 = bbox
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            crop = frame
        
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        h, w = self.model.input_shape[1], self.model.input_shape[2]
        resized = cv2.resize(crop_rgb, (w, h), interpolation=cv2.INTER_AREA)
        arr = resized.astype(np.float32) / 255.0
        return np.expand_dims(arr, axis=0)

    def speak_once(self, text):
        """Text-to-speech function"""
        def _run():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

    def play_alarm(self):
        """Play alarm sound"""
        if os.path.exists(ALARM_FILE):
            threading.Thread(target=lambda: self.__play(ALARM_FILE), daemon=True).start()
        else:
            print("Alarm file missing:", ALARM_FILE)

    def __play(self, path):
        """Play sound file"""
        try:
            from playsound import playsound
            playsound(path)
        except Exception as e:
            print("playsound failed:", e)

    def popup(self, message):
        """Show popup alert"""
        if os.path.exists(POPUP_SCRIPT):
            try:
                subprocess.Popen(['cscript', '//Nologo', POPUP_SCRIPT, message])
            except Exception as e:
                print("Popup failed:", e)
        else:
            print("Popup script not found, message:", message)

    def log_fall(self, event_info):
        """Log fall event"""
        try:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(event_info) + "\n")
        except Exception as e:
            print("Failed to log:", e)

    def on_fall_detected(self, frame, bbox, prob):
        """Handle fall detection"""
        t = time.time()
        ts = time.ctime(t)
        print("[ALERT] Fall detected @", ts, "prob:", prob)
        
        # Update UI
        self.fall_detected = True
        self.alert_active = True
        self.previous_falls += 1
        
        self.status_label.config(text="⚠️ Status: FALL DETECTED!", foreground='#ff6600')
        self.voice_status.config(text="Voice: 'Are you okay?'")
        self.falls_label.config(text=f"Previous Falls: {self.previous_falls}")
        
        # Play alarm + voice + popup
        self.play_alarm()
        self.speak_once("Attention. Fall detected. Are you okay?")
        threading.Thread(target=lambda: self.popup("Fall detected! Are you okay?"), daemon=True).start()
        
        # Save snapshot
        x1, y1, x2, y2 = bbox
        try:
            os.makedirs("captures", exist_ok=True)
            fname = f"captures/fall_{int(t)}.jpg"
            cv2.imwrite(fname, frame)
        except Exception as e:
            print("Failed to save capture:", e)
        
        # Log event
        event = {"timestamp": t, "time_str": ts, "prob": float(prob)}
        self.log_fall(event)

    def update_health_data(self):
        """Simulate health data updates"""
        self.heart_rate += np.random.randint(-2, 3)
        self.heart_rate = max(60, min(100, self.heart_rate))
        self.current_time = datetime.now()
        
        self.hr_label.config(text=f"{self.heart_rate} BPM")
        self.time_label.config(text=f"Time: {self.current_time.strftime('%H:%M:%S')}")

    def simulate_fall(self):
        """Simulate a fall for testing"""
        self.fall_detected = True
        self.alert_active = True
        self.previous_falls += 1
        self.status_label.config(text="⚠️ Status: FALL DETECTED!", foreground='#ff6600')
        self.voice_status.config(text="Voice: 'Are you okay?'")
        self.falls_label.config(text=f"Previous Falls: {self.previous_falls}")
        
        # Trigger alerts
        self.play_alarm()
        self.speak_once("Attention. Fall detected. Are you okay?")
        threading.Thread(target=lambda: self.popup("Fall detected! Are you okay?"), daemon=True).start()

    def cancel_alert(self):
        """Cancel false alarm"""
        self.alert_active = False
        self.fall_detected = False
        self.status_label.config(text="✅ Status: Normal", foreground='#00ff00')
        self.voice_status.config(text="Voice: 'Alert cancelled. Thank you!'")
        self.speak_once("Alert cancelled. Thank you for confirming.")

    def reset_system(self):
        """Reset the entire system"""
        self.fall_detected = False
        self.alert_active = False
        self.previous_falls = 0
        self.sustain = 0
        self.pred_buf.clear()
        
        self.status_label.config(text="✅ Status: Normal", foreground='#00ff00')
        self.voice_status.config(text="Voice: Ready")
        self.falls_label.config(text=f"Previous Falls: {self.previous_falls}")
        self.fall_prob_label.config(text="Fall Probability: 0.00")

    def process_video(self):
        """Main video processing loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        frame_interval = 1.0 / FPS_TARGET
        last_frame_time = 0
        fps_counter = 0
        fps_start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            now = time.time()
            if now - last_frame_time < frame_interval:
                continue
            last_frame_time = now
            
            h, w = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(img)
            landmarks = results.pose_landmarks.landmark if results.pose_landmarks else None
            
            fall_prob = 0.0
            label_text = "No person"
            
            if landmarks and self.model:
                # Get bounding box
                bbox = self.landmarks_bbox(landmarks, w, h, pad=0.5)
                
                # Preprocess crop and predict
                x = self.preprocess_crop_for_model(frame, bbox)
                try:
                    preds = self.model.predict(x, verbose=0)
                    if preds.ndim == 2 and preds.shape[1] >= 2:
                        fall_prob = float(preds[0, 1])
                    else:
                        fall_prob = float(preds.ravel()[-1])
                except Exception as e:
                    print("Model prediction failed:", e)
                    fall_prob = 0.0
                
                # Smoothing buffer
                self.pred_buf.append(fall_prob)
                avg_prob = float(np.mean(self.pred_buf))
                label_text = f"FallProb:{avg_prob:.2f}"
                
                # Check threshold + sustain
                if avg_prob >= FALL_PROB_THRESHOLD:
                    self.sustain += 1
                else:
                    self.sustain = max(0, self.sustain - 1)
                
                if self.sustain >= SUSTAIN_REQUIRED and (now - self.last_alert_time) > 6:
                    # Confirmed fall
                    self.last_alert_time = now
                    self.sustain = 0
                    self.on_fall_detected(frame, bbox, avg_prob)
                
                # Update UI
                self.fall_prob_label.config(text=f"Fall Probability: {avg_prob:.2f}")
            
            # Draw landmarks and UI
            vis = frame.copy()
            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(vis, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            # Show bounding box
            if landmarks:
                x1, y1, x2, y2 = self.landmarks_bbox(landmarks, w, h, pad=0.5)
                cv2.rectangle(vis, (x1, y1), (x2, y2), (180, 50, 50), 2)
            
            cv2.putText(vis, label_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter % 10 == 0:
                fps = fps_counter / (now - fps_start_time)
                fps_counter = 0
                fps_start_time = now
                self.fps_label.config(text=f"FPS: {fps:.1f}")
            
            cv2.putText(vis, f"FPS: {FPS_TARGET}", (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Convert frame for display
            frame_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update video display
            video_label = tk.Label(self.video_frame, image=frame_tk, bg='#2d2d2d')
            video_label.image = frame_tk
            video_label.pack()
            
            # Update health data
            self.update_health_data()
            
            # Break on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def run(self):
        """Start the application"""
        # Start video processing in separate thread
        video_thread = threading.Thread(target=self.process_video, daemon=True)
        video_thread.start()
        
        # Start the GUI
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedFallDetectionSystem()
    app.run()
