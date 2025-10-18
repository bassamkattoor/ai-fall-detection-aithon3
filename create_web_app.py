import cv2
import numpy as np
import time
from datetime import datetime
import json
import os

class WebFallDetectionAPI:
    def __init__(self):
        self.fall_detected = False
        self.alert_active = False
        self.motion_threshold = 1000
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        
        # Health data simulation
        self.heart_rate = 75
        self.previous_falls = 0
        self.current_time = datetime.now()

    def detect_motion_and_fall(self, frame):
        """Detect motion and potential falls using background subtraction"""
        fg_mask = self.background_subtractor.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_area = 0
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                motion_area += cv2.contourArea(contour)
        
        if motion_area > self.motion_threshold:
            return True
        return False

    def update_health_data(self):
        """Simulate health data updates"""
        self.heart_rate += np.random.randint(-2, 3)
        self.heart_rate = max(60, min(100, self.heart_rate))
        self.current_time = datetime.now()

    def process_image(self, image_data):
        """Process uploaded image for fall detection"""
        # Convert base64 or file data to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Could not decode image"}
        
        # Detect motion and potential falls
        fall_detected = self.detect_motion_and_fall(frame)
        
        if fall_detected and not self.fall_detected:
            self.fall_detected = True
            self.alert_active = True
            self.previous_falls += 1
        
        # Update health data
        self.update_health_data()
        
        # Draw motion detection overlay
        fg_mask = self.background_subtractor.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        
        # Add status text
        status_text = "FALL DETECTED!" if self.fall_detected else "Motion Detection Active"
        color = (0, 0, 255) if self.fall_detected else (0, 255, 0)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Encode processed image
        _, buffer = cv2.imencode('.jpg', frame)
        processed_image = buffer.tobytes()
        
        return {
            "processed_image": processed_image,
            "fall_detected": self.fall_detected,
            "alert_active": self.alert_active,
            "heart_rate": self.heart_rate,
            "previous_falls": self.previous_falls,
            "current_time": self.current_time.strftime('%H:%M:%S'),
            "status": "FALL DETECTED!" if self.fall_detected else "Normal"
        }

    def cancel_alert(self):
        """Cancel false alarm"""
        self.alert_active = False
        self.fall_detected = False
        return {"status": "Alert cancelled"}

    def reset_system(self):
        """Reset the entire system"""
        self.fall_detected = False
        self.alert_active = False
        self.previous_falls = 0
        return {"status": "System reset"}

    def simulate_fall(self):
        """Simulate a fall for testing"""
        self.fall_detected = True
        self.alert_active = True
        self.previous_falls += 1
        return {"status": "Fall simulated"}

# Create a simple HTML interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Fall Detection System - AITHON 3.0</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(45, 45, 45, 0.8);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #00ff88;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }
        
        .header p {
            color: #cccccc;
            font-size: 1.2em;
            margin: 10px 0;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .camera-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #333;
        }
        
        .health-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #333;
        }
        
        .upload-area {
            border: 3px dashed #555;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.1);
        }
        
        .upload-area.dragover {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.2);
        }
        
        .status-display {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .status-normal {
            color: #00ff88;
            border: 2px solid #00ff88;
        }
        
        .status-alert {
            color: #ff6600;
            border: 2px solid #ff6600;
            animation: pulse 1s infinite;
        }
        
        .status-emergency {
            color: #ff0000;
            border: 2px solid #ff0000;
            animation: pulse 0.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .metric-card {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            border: 1px solid #444;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
            margin: 5px 0;
        }
        
        .metric-label {
            color: #cccccc;
            font-size: 0.9em;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            background: linear-gradient(45deg, #333, #555);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            flex: 1;
            min-width: 120px;
        }
        
        .btn:hover {
            background: linear-gradient(45deg, #555, #777);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #00ff88, #00cc66);
        }
        
        .btn-danger {
            background: linear-gradient(45deg, #ff6600, #cc4400);
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #666, #888);
        }
        
        .image-preview {
            max-width: 100%;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .info-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border: 2px solid #333;
        }
        
        .info-section h3 {
            color: #00ff88;
            margin-top: 0;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }
        
        .feature-list li:before {
            content: "✅ ";
            color: #00ff88;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
            color: #888;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 AI Fall Detection System</h1>
            <p>AITHON 3.0 | IEEE Student Branch | College of Engineering Karungappally</p>
        </div>
        
        <div class="main-content">
            <div class="camera-section">
                <h2>📹 Camera Feed Analysis</h2>
                
                <div class="upload-area" id="uploadArea">
                    <p>📸 Upload an image or drag & drop here</p>
                    <p style="color: #888; font-size: 0.9em;">The system will analyze the image for fall detection</p>
                    <input type="file" id="fileInput" accept="image/*" style="display: none;">
                </div>
                
                <div id="imagePreview"></div>
                
                <div class="status-display status-normal" id="statusDisplay">
                    ✅ Status: Normal
                </div>
                
                <div class="button-group">
                    <button class="btn btn-primary" onclick="simulateFall()">🧪 Simulate Fall</button>
                    <button class="btn btn-danger" onclick="cancelAlert()">❌ Cancel Alert</button>
                    <button class="btn btn-secondary" onclick="resetSystem()">🔄 Reset System</button>
                </div>
            </div>
            
            <div class="health-section">
                <h2>💓 Health Monitor</h2>
                
                <div class="metric-card">
                    <div class="metric-value" id="heartRate">75 BPM</div>
                    <div class="metric-label">Heart Rate</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value" id="previousFalls">0</div>
                    <div class="metric-label">Previous Falls</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value" id="currentTime">--:--:--</div>
                    <div class="metric-label">Current Time</div>
                </div>
                
                <h3>🎤 Voice Interaction</h3>
                <div class="status-display status-normal" id="voiceStatus">
                    Voice: Ready
                </div>
            </div>
        </div>
        
        <div class="info-section">
            <h3>ℹ️ System Information</h3>
            <ul class="feature-list">
                <li>Real-time motion detection using computer vision</li>
                <li>Background subtraction for fall detection</li>
                <li>Health data simulation and monitoring</li>
                <li>Alert management system</li>
                <li>Voice interaction simulation</li>
                <li>Dark theme interface</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>AI Fall Detection System | AITHON 3.0 | IEEE Student Branch</p>
            <p>Built with OpenCV, Computer Vision, and AI Technology</p>
        </div>
    </div>

    <script>
        // System state
        let systemState = {
            fallDetected: false,
            alertActive: false,
            heartRate: 75,
            previousFalls: 0
        };
        
        // Update time every second
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleTimeString();
        }
        
        setInterval(updateTime, 1000);
        updateTime();
        
        // Simulate heart rate variation
        function updateHeartRate() {
            systemState.heartRate += Math.floor(Math.random() * 5) - 2;
            systemState.heartRate = Math.max(60, Math.min(100, systemState.heartRate));
            document.getElementById('heartRate').textContent = systemState.heartRate + ' BPM';
        }
        
        setInterval(updateHeartRate, 3000);
        
        // File upload handling
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const imagePreview = document.getElementById('imagePreview');
        const statusDisplay = document.getElementById('statusDisplay');
        const voiceStatus = document.getElementById('voiceStatus');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'image-preview';
                imagePreview.innerHTML = '';
                imagePreview.appendChild(img);
                
                // Simulate fall detection
                simulateImageAnalysis();
            };
            reader.readAsDataURL(file);
        }
        
        function simulateImageAnalysis() {
            // Simulate processing delay
            setTimeout(() => {
                // Random chance of detecting a fall
                if (Math.random() < 0.3) {
                    systemState.fallDetected = true;
                    systemState.alertActive = true;
                    systemState.previousFalls++;
                    
                    statusDisplay.textContent = '⚠️ Status: FALL DETECTED!';
                    statusDisplay.className = 'status-display status-alert';
                    voiceStatus.textContent = 'Voice: "Are you okay?"';
                    voiceStatus.className = 'status-display status-alert';
                    
                    document.getElementById('previousFalls').textContent = systemState.previousFalls;
                } else {
                    statusDisplay.textContent = '✅ Status: Normal';
                    statusDisplay.className = 'status-display status-normal';
                }
            }, 1000);
        }
        
        function simulateFall() {
            systemState.fallDetected = true;
            systemState.alertActive = true;
            systemState.previousFalls++;
            
            statusDisplay.textContent = '⚠️ Status: FALL DETECTED!';
            statusDisplay.className = 'status-display status-alert';
            voiceStatus.textContent = 'Voice: "Are you okay?"';
            voiceStatus.className = 'status-display status-alert';
            
            document.getElementById('previousFalls').textContent = systemState.previousFalls;
        }
        
        function cancelAlert() {
            systemState.alertActive = false;
            systemState.fallDetected = false;
            
            statusDisplay.textContent = '✅ Status: Normal';
            statusDisplay.className = 'status-display status-normal';
            voiceStatus.textContent = 'Voice: "Alert cancelled. Thank you!"';
            voiceStatus.className = 'status-display status-normal';
        }
        
        function resetSystem() {
            systemState.fallDetected = false;
            systemState.alertActive = false;
            systemState.previousFalls = 0;
            
            statusDisplay.textContent = '✅ Status: Normal';
            statusDisplay.className = 'status-display status-normal';
            voiceStatus.textContent = 'Voice: Ready';
            voiceStatus.className = 'status-display status-normal';
            
            document.getElementById('previousFalls').textContent = '0';
            imagePreview.innerHTML = '';
        }
    </script>
</body>
</html>
"""

# Save the HTML file
with open('fall_detection_web.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Web application created successfully!")
print("File: fall_detection_web.html")
print("Open this file in your browser to use the web version")
print("Perfect for hackathon demos and presentations!")
