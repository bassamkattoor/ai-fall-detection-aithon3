import cv2
import time
import threading
import os
import json
import numpy as np
import mediapipe as mp
import pyttsx3
from collections import deque
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

class AdvancedFallDetectionSystem:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Fall detection parameters
        self.pred_buf = deque(maxlen=6)
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
        self.model_status = ttk.Label(left_panel, text="⚠️ AI Model: Using Pose-Based Detection", style='Dark.TLabel', font=('Arial', 12))
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
        
    def detect_fall_from_pose(self, landmarks):
        """Detect fall using pose landmarks (fallback when no model)"""
        if not landmarks:
            return 0.0
            
        try:
            # Get key points
            nose = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            # Calculate body orientation
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2
            
            # Check if body is horizontal (fall indicator)
            body_angle = abs(shoulder_center_y - hip_center_y)
            
            # Check if person is on the ground (low y-coordinate)
            ground_threshold = 0.8
            is_on_ground = nose.y > ground_threshold
            
            # Calculate fall probability based on pose
            fall_prob = 0.0
            if body_angle < 0.3 and is_on_ground:
                fall_prob = 0.8  # High probability of fall
            elif body_angle < 0.5:
                fall_prob = 0.4  # Medium probability
            elif is_on_ground:
                fall_prob = 0.2  # Low probability
                
            return fall_prob
            
        except Exception as e:
            print(f"Error in pose-based fall detection: {e}")
            return 0.0

    def speak_once(self, text):
        """Text-to-speech function"""
        def _run():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

    def on_fall_detected(self, frame, prob):
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
        
        # Play voice alert
        self.speak_once("Attention. Fall detected. Are you okay?")
        
        # Save snapshot
        try:
            os.makedirs("captures", exist_ok=True)
            fname = f"captures/fall_{int(t)}.jpg"
            cv2.imwrite(fname, frame)
        except Exception as e:
            print("Failed to save capture:", e)
        
        # Log event
        event = {"timestamp": t, "time_str": ts, "prob": float(prob)}
        try:
            with open("fall_log.txt", "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print("Failed to log:", e)

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
        self.speak_once("Attention. Fall detected. Are you okay?")

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
        
        fps_counter = 0
        fps_start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            h, w = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(img)
            landmarks = results.pose_landmarks.landmark if results.pose_landmarks else None
            
            fall_prob = 0.0
            label_text = "No person"
            
            if landmarks:
                # Use pose-based fall detection
                fall_prob = self.detect_fall_from_pose(landmarks)
                
                # Smoothing buffer
                self.pred_buf.append(fall_prob)
                avg_prob = float(np.mean(self.pred_buf))
                label_text = f"FallProb:{avg_prob:.2f}"
                
                # Check threshold + sustain
                if avg_prob >= 0.6:  # Threshold for pose-based detection
                    self.sustain += 1
                else:
                    self.sustain = max(0, self.sustain - 1)
                
                if self.sustain >= 3 and (time.time() - self.last_alert_time) > 6:
                    # Confirmed fall
                    self.last_alert_time = time.time()
                    self.sustain = 0
                    self.on_fall_detected(frame, avg_prob)
                
                # Update UI
                self.fall_prob_label.config(text=f"Fall Probability: {avg_prob:.2f}")
            
            # Draw landmarks and UI
            vis = frame.copy()
            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(vis, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter % 10 == 0:
                fps = fps_counter / (time.time() - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
                self.fps_label.config(text=f"FPS: {fps:.1f}")
            
            cv2.putText(vis, label_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(vis, f"FPS: {fps:.1f}", (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
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
