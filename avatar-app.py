import sys
import os
import threading
import time
import numpy as np
import pygame
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap, QPainter, QImage
import cv2
from PIL import Image, ImageQt

class VoiceGenerator(QObject):
    finished = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        # Set up an attractive female voice
        voices = self.engine.getProperty('voices')
        # Try to find a female voice in the available voices
        female_voice = None
        for voice in voices:
            if "female" in voice.name.lower():
                female_voice = voice.id
                break
        
        # If no explicitly female voice is found, try to use the second voice (often female)
        if female_voice is None and len(voices) > 1:
            female_voice = voices[1].id
        # Otherwise use whatever voice is available
        elif female_voice is None and len(voices) > 0:
            female_voice = voices[0].id
            
        if female_voice:
            self.engine.setProperty('voice', female_voice)
        
        # Adjust voice properties for an attractive sound
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
    def speak_text(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
        self.finished.emit("Speech completed")

class LipSyncAnimator:
    def __init__(self):
        # Load the avatar base image
        self.base_image = cv2.imread("avatar_base.jpg")
        if self.base_image is None:
            # Create a placeholder image if no avatar is available
            self.base_image = np.ones((600, 400, 3), dtype=np.uint8) * 255
            cv2.putText(self.base_image, "Avatar", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Create different mouth shapes for lip sync
        self.mouth_shapes = {
            "rest": self.base_image.copy(),
            "slight_open": self.create_mouth_shape("slight"),
            "medium_open": self.create_mouth_shape("medium"),
            "wide_open": self.create_mouth_shape("wide")
        }
        
        self.current_frame = self.mouth_shapes["rest"]
        
    def create_mouth_shape(self, shape_type):
        # This is a simplified version. In a real implementation,
        # you would have actual mouth shape images or modify the base image
        # to change the mouth shape according to phonemes
        img = self.base_image.copy()
        
        # Here, we're just putting text to show different states
        # In a real app, you would modify the mouth region of the avatar
        y_pos = 400
        if shape_type == "slight":
            cv2.putText(img, "•", (200, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif shape_type == "medium":
            cv2.putText(img, "o", (200, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif shape_type == "wide":
            cv2.putText(img, "O", (200, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return img
    
    def get_frame_for_phoneme(self, phoneme):
        # Map phonemes to mouth shapes
        # This is a simplified version. A real implementation would
        # map different phonemes to appropriate mouth shapes
        vowels = ['a', 'e', 'i', 'o', 'u']
        plosives = ['p', 'b', 'm']
        
        if phoneme.lower() in vowels:
            return self.mouth_shapes["medium_open"]
        elif phoneme.lower() in plosives:
            return self.mouth_shapes["wide_open"]
        else:
            return self.mouth_shapes["slight_open"]
    
    def animate_speech(self, text):
        # Simple animation: cycle through mouth positions based on text
        frames = []
        for char in text:
            if char.isalpha():
                frames.append(self.get_frame_for_phoneme(char))
            else:
                frames.append(self.mouth_shapes["rest"])
                
        return frames

class AvatarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Assistant")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Make window stay on top
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Avatar display area
        self.avatar_label = QLabel()
        self.avatar_label.setMinimumSize(400, 600)
        main_layout.addWidget(self.avatar_label)
        
        # Text input area
        input_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setMaximumHeight(100)
        input_layout.addWidget(self.text_input)
        
        # Speak button
        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.process_speech)
        input_layout.addWidget(self.speak_button)
        
        main_layout.addLayout(input_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Initialize lip sync animator
        self.lip_sync = LipSyncAnimator()
        self.avatar_label.setPixmap(self.convert_cv_to_pixmap(self.lip_sync.current_frame))
        
        # Voice generator setup
        self.voice_thread = QThread()
        self.voice_generator = VoiceGenerator()
        self.voice_generator.moveToThread(self.voice_thread)
        self.voice_generator.finished.connect(self.speech_finished)
        self.voice_thread.start()
        
        # Animation timer
        self.animation_frames = []
        self.current_frame_idx = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.is_speaking = False
        
    def convert_cv_to_pixmap(self, cv_img):
        # Convert OpenCV image to QPixmap for display
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(q_img)
        
    def process_speech(self):
        if self.is_speaking:
            return
            
        text = self.text_input.toPlainText().strip()
        if not text:
            return
            
        self.is_speaking = True
        self.speak_button.setEnabled(False)
        
        # Generate animation frames for the text
        self.animation_frames = self.lip_sync.animate_speech(text)
        self.current_frame_idx = 0
        
        # Start animation
        self.animation_timer.start(100)  # Update every 100ms
        
        # Start speech in another thread
        threading.Thread(target=self.voice_generator.speak_text, args=(text,)).start()
    
    def update_animation(self):
        if not self.animation_frames or self.current_frame_idx >= len(self.animation_frames):
            self.animation_timer.stop()
            # Return to rest pose
            self.avatar_label.setPixmap(self.convert_cv_to_pixmap(self.lip_sync.mouth_shapes["rest"]))
            return
            
        # Update avatar with current frame
        frame = self.animation_frames[self.current_frame_idx]
        self.avatar_label.setPixmap(self.convert_cv_to_pixmap(frame))
        self.current_frame_idx += 1
    
    def speech_finished(self, message):
        self.is_speaking = False
        self.speak_button.setEnabled(True)
        self.animation_timer.stop()
        # Reset to rest position
        self.avatar_label.setPixmap(self.convert_cv_to_pixmap(self.lip_sync.mouth_shapes["rest"]))
    
    def closeEvent(self, event):
        self.voice_thread.quit()
        self.voice_thread.wait()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = AvatarApp()
    window.resize(400, 700)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
