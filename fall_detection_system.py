import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time
import json
from datetime import datetime
import pyttsx3
import speech_recognition as sr

class FallDetectionSystem:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Fall detection parameters
        self.fall_threshold = 0.3  # Threshold for detecting falls
        self.inactivity_threshold = 3.0  # Seconds of inactivity
        self.last_movement_time = time.time()
        self.fall_detected = False
        self.alert_active = False
        
        # Health data simulation
        self.heart_rate = 75
        self.previous_falls = 0
        self.current_time = datetime.now()
        
        # Voice system
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the dark-themed UI"""
        self.root = tk.Tk()
        self.root.title("AI Fall Detection System - AITHON 3.0")
        self.root.configure(bg='#1a1a1a')
        self.root.geometry("1200x800")
        
        # Configure dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='#ffffff')
        style.configure('Dark.TFrame', background='#1a1a1a')
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Camera feed
        left_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Camera feed label
        self.camera_label = ttk.Label(left_panel, text="Camera Feed", style='Dark.TLabel', font=('Arial', 14, 'bold'))
        self.camera_label.pack(pady=(0, 10))
        
        # Video display
        self.video_frame = tk.Frame(left_panel, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status display
        self.status_label = ttk.Label(left_panel, text="Status: Normal", style='Dark.TLabel', font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # Right panel - Health data
        right_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Heart rate monitor
        hr_frame = ttk.LabelFrame(right_panel, text="Heart Rate Monitor", style='Dark.TFrame')
        hr_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hr_label = ttk.Label(hr_frame, text=f"{self.heart_rate} BPM", style='Dark.TLabel', font=('Arial', 24, 'bold'))
        self.hr_label.pack(pady=20)
        
        # Previous data
        data_frame = ttk.LabelFrame(right_panel, text="Health Data", style='Dark.TFrame')
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.falls_label = ttk.Label(data_frame, text=f"Previous Falls: {self.previous_falls}", style='Dark.TLabel')
        self.falls_label.pack(pady=5)
        
        self.time_label = ttk.Label(data_frame, text=f"Time: {self.current_time.strftime('%H:%M:%S')}", style='Dark.TLabel')
        self.time_label.pack(pady=5)
        
        # Alert controls
        alert_frame = ttk.LabelFrame(right_panel, text="Alert Controls", style='Dark.TFrame')
        alert_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cancel_button = ttk.Button(alert_frame, text="Cancel False Alarm", command=self.cancel_alert)
        self.cancel_button.pack(pady=10)
        
        # Voice interaction
        voice_frame = ttk.LabelFrame(right_panel, text="Voice Interaction", style='Dark.TFrame')
        voice_frame.pack(fill=tk.X)
        
        self.voice_status = ttk.Label(voice_frame, text="Voice: Ready", style='Dark.TLabel')
        self.voice_status.pack(pady=5)
        
    def detect_fall(self, landmarks):
        """Detect fall based on pose landmarks"""
        if not landmarks:
            return False
            
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
        
        # Fall detection logic
        if body_angle < self.fall_threshold and is_on_ground:
            return True
            
        return False
        
    def update_health_data(self):
        """Simulate health data updates"""
        # Simulate heart rate variation
        self.heart_rate += np.random.randint(-2, 3)
        self.heart_rate = max(60, min(100, self.heart_rate))
        
        # Update time
        self.current_time = datetime.now()
        
        # Update UI
        self.hr_label.config(text=f"{self.heart_rate} BPM")
        self.time_label.config(text=f"Time: {self.current_time.strftime('%H:%M:%S')}")
        
    def speak(self, text):
        """Text-to-speech function"""
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        threading.Thread(target=speak_thread, daemon=True).start()
        
    def listen_for_response(self):
        """Listen for user voice response"""
        def listen_thread():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.voice_status.config(text="Voice: Listening...")
                    audio = self.recognizer.listen(source, timeout=5)
                    
                response = self.recognizer.recognize_google(audio).lower()
                self.voice_status.config(text=f"Voice: Heard '{response}'")
                
                # Process response
                if any(word in response for word in ['fine', 'okay', 'good', 'yes']):
                    self.cancel_alert()
                elif any(word in response for word in ['help', 'emergency', 'no']):
                    self.escalate_alert()
                    
            except sr.UnknownValueError:
                self.voice_status.config(text="Voice: Could not understand")
            except sr.RequestError:
                self.voice_status.config(text="Voice: Service unavailable")
                
        threading.Thread(target=listen_thread, daemon=True).start()
        
    def cancel_alert(self):
        """Cancel false alarm"""
        self.alert_active = False
        self.fall_detected = False
        self.status_label.config(text="Status: Normal", foreground='#00ff00')
        self.speak("Alert cancelled. Thank you for confirming.")
        
    def escalate_alert(self):
        """Escalate alert to emergency contacts"""
        self.status_label.config(text="Status: EMERGENCY ALERT SENT", foreground='#ff0000')
        self.speak("Emergency alert has been sent to your contacts.")
        # Here you would implement actual alert sending (email, SMS, etc.)
        
    def process_video(self):
        """Main video processing loop"""
        cap = cv2.VideoCapture(0)  # Use webcam
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process pose
            results = self.pose.process(rgb_frame)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                
                # Check for fall
                if self.detect_fall(results.pose_landmarks):
                    if not self.fall_detected:
                        self.fall_detected = True
                        self.alert_active = True
                        self.status_label.config(text="Status: FALL DETECTED!", foreground='#ff6600')
                        self.speak("I detected a potential fall. Are you okay?")
                        self.listen_for_response()
                        
                        # Update fall count
                        self.previous_falls += 1
                        self.falls_label.config(text=f"Previous Falls: {self.previous_falls}")
                else:
                    if self.fall_detected and not self.alert_active:
                        self.fall_detected = False
                        self.status_label.config(text="Status: Normal", foreground='#00ff00')
                        
            # Convert frame for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
    from PIL import Image, ImageTk
    app = FallDetectionSystem()
    app.run()
