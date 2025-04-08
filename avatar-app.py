import sys
import os
import threading
import time
import numpy as np
import pyttsx3
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit, QHBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap, QPainter
import cv2
import trimesh
import pyrender
import speech_recognition as sr

# For blendshape animations
from scipy.spatial.transform import Rotation as R
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from pywavefront import Wavefront

female_head = os.path.join(os.path.join(os.getcwd(), "ressources"), "female_red_head.obj")

class VoiceGenerator(QObject):
    finished = pyqtSignal(str)
    phoneme_signal = pyqtSignal(str, float)  # Phoneme and its duration
    
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
        
        # Set up callback for word and phoneme events
        self.engine.connect('started-word', self.on_word)
        
        # Phoneme mapping for lip sync
        self.phoneme_map = {
            'AA': 'ah', 'AE': 'ae', 'AH': 'ah', 'AO': 'oh',
            'AW': 'aw', 'AY': 'ay', 'B': 'b', 'CH': 'ch',
            'D': 'd', 'DH': 'th', 'EH': 'eh', 'ER': 'er',
            'EY': 'ey', 'F': 'f', 'G': 'g', 'HH': 'h',
            'IH': 'ih', 'IY': 'ee', 'JH': 'j', 'K': 'k',
            'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ng',
            'OW': 'oh', 'OY': 'oy', 'P': 'p', 'R': 'r',
            'S': 's', 'SH': 'sh', 'T': 't', 'TH': 'th',
            'UH': 'uh', 'UW': 'oo', 'V': 'v', 'W': 'w',
            'Y': 'y', 'Z': 'z', 'ZH': 'zh'
        }
    
    def on_word(self, name, location, length):
        # This would be called when a word starts
        # In a production app, you'd use more sophisticated phoneme extraction
        pass
        
    def speak_text(self, text):
        # For better phoneme extraction in a real app, you would:
        # 1. Use a dedicated phoneme extractor library
        # 2. Or use a TTS service that provides phoneme timing data
        
        # Simple simulation of phoneme extraction for demonstration
        phonemes = self.simple_phoneme_extraction(text)
        
        # Emit phonemes with timing for lip sync
        for phoneme, duration in phonemes:
            self.phoneme_signal.emit(phoneme, duration)
            time.sleep(duration)  # Simulate the timing
        
        # Actually speak the text
        self.engine.say(text)
        self.engine.runAndWait()
        self.finished.emit("Speech completed")
    
    def simple_phoneme_extraction(self, text):
        # Very simplified phoneme extraction
        # In a real application, use a dedicated library like CMU Sphinx
        phonemes = []
        for char in text:
            if char.lower() in 'aeiou':
                # Vowels - longer duration
                phonemes.append((char.lower(), 0.15))
            elif char.isalpha():
                # Consonants - shorter duration
                phonemes.append((char.lower(), 0.08))
            else:
                # Pauses
                phonemes.append(('rest', 0.1))
        return phonemes

class Model3D:
    def __init__(self):
        # Initialize the 3D rendering components
        self.scene = pyrender.Scene(ambient_light=[0.5, 0.5, 0.5])
        
        # In a real application, you would load your 3D model here
        # For demonstration, we'll create a simple face mesh
        self.mesh = self.create_face_mesh()
        self.mesh_node = pyrender.Node(mesh=self.mesh, matrix=np.eye(4))
        self.scene.add_node(self.mesh_node)
        
        # Setup camera
        self.camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
        self.camera_pose = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.5],
            [0.0, 0.0, 0.0, 1.0],
        ])
        self.scene.add(self.camera, pose=self.camera_pose)
        
        # Setup light
        light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)
        self.scene.add(light, pose=self.camera_pose)
        
        # Blendshapes for facial animation
        self.blendshapes = {
            'rest': np.zeros(self.mesh.primitives[0].positions.shape),
            'smile': self.create_blend_shape('smile'),
            'ah': self.create_blend_shape('ah'),
            'oh': self.create_blend_shape('oh'),
            'ee': self.create_blend_shape('ee'),
            'f': self.create_blend_shape('f'),
            'm': self.create_blend_shape('m'),
            'l': self.create_blend_shape('l')
        }
        
        # Current blendshape weights
        self.current_weights = {shape: 0.0 for shape in self.blendshapes}
        self.current_weights['rest'] = 1.0
        
        # Renderer for offscreen rendering
        self.renderer = pyrender.OffscreenRenderer(400, 600)
    
    def create_face_mesh(self):
        # In a real application, you would load a 3D model from a file
        # For demonstration, we'll create a simple face mesh
        # This is highly simplified - in a real app, you'd use an actual 3D model file
        
        try:
            # Try to load an actual model if available
            mesh = trimesh.load(female_head)
            return pyrender.Mesh.from_trimesh(mesh)
        except:
            # Fallback to a simple primitive
            box = trimesh.creation.box()
            mesh = pyrender.Mesh.from_trimesh(box)
            return mesh
    
    def create_blend_shape(self, shape_type):
        # In a real application, these would be loaded from a file with proper facial blendshapes
        # This is just for demonstration
        base_positions = self.mesh.primitives[0].positions.copy()
        
        # Simple vertex modifications based on shape type
        if shape_type == 'smile':
            # Move some vertices to form a smile
            pass
        elif shape_type == 'ah':
            # Open mouth for 'ah' sound
            pass
        elif shape_type == 'oh':
            # Round mouth for 'oh' sound
            pass
        
        # Return the displacement from base positions
        return base_positions
    
    def update_for_phoneme(self, phoneme):
        # Reset weights
        for shape in self.current_weights:
            self.current_weights[shape] = 0.0
        
        # Set appropriate blendshape weights based on phoneme
        if phoneme in ['a', 'ah', 'ae']:
            self.current_weights['ah'] = 1.0
        elif phoneme in ['o', 'oh', 'ow']:
            self.current_weights['oh'] = 1.0
        elif phoneme in ['e', 'ee']:
            self.current_weights['ee'] = 1.0
        elif phoneme in ['f', 'v']:
            self.current_weights['f'] = 1.0
        elif phoneme in ['m', 'b', 'p']:
            self.current_weights['m'] = 1.0
        elif phoneme in ['l']:
            self.current_weights['l'] = 1.0
        else:
            self.current_weights['rest'] = 1.0
        
        # Apply blendshape weights
        self.apply_blendshapes()
    
    def apply_blendshapes(self):
        # Calculate vertex positions based on blendshape weights
        final_positions = np.zeros_like(self.mesh.primitives[0].positions)
        
        for shape, weight in self.current_weights.items():
            final_positions += self.blendshapes[shape] * weight
        
        # Update mesh vertices
        self.mesh.primitives[0].positions = final_positions
        
        # Update mesh in scene
        self.scene.remove_node(self.mesh_node)
        self.mesh_node = pyrender.Node(mesh=self.mesh, matrix=np.eye(4))
        self.scene.add_node(self.mesh_node)
    
    def render(self):
        # Render the scene
        color, depth = self.renderer.render(self.scene)
        return color

class AvatarOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(AvatarOpenGLWidget, self).__init__(parent)
        self.model = None
        self.texture = None
        
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        
        # Initialize model
        self.init_model()
        
    def init_model(self):
        try:
            # Try to load the model
            self.model = Wavefront(female_head)
        except:
            # Handle case where model can't be loaded
            print("Could not load 3D model. Using fallback.")
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Position the model
        glTranslatef(0.0, 0.0, -5.0)
        
        # Rotate model to face camera
        glRotatef(180, 0, 0, 1)
        
        # Draw the model if available
        if self.model:
            self.draw_model()
        else:
            self.draw_fallback()
    
    def draw_model(self):
        # Draw the actual 3D model
        # This is simplified - in a real app, you'd use shaders and proper rendering
        for mesh in self.model.meshes:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    vertex = mesh.vertices[vertex_i]
                    glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
    
    def draw_fallback(self):
        # Draw a simple cube as fallback
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # And other faces...
        glEnd()
        
    def update_face_for_phoneme(self, phoneme):
        # Update facial expression based on phoneme
        # This would modify the vertices or blend shapes of the model
        # Example implementation depends on your model format
        self.update()

class AvatarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Avatar Assistant")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Make window stay on top
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Avatar display area - now using OpenGL for 3D rendering
        self.avatar_view = AvatarOpenGLWidget()
        self.avatar_view.setMinimumSize(400, 600)
        main_layout.addWidget(self.avatar_view)
        
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
        
        # Initialize 3D model
        self.model_3d = Model3D()
        
        # Voice generator setup
        self.voice_thread = QThread()
        self.voice_generator = VoiceGenerator()
        self.voice_generator.moveToThread(self.voice_thread)
        self.voice_generator.finished.connect(self.speech_finished)
        self.voice_generator.phoneme_signal.connect(self.on_phoneme)
        self.voice_thread.start()
        
        self.is_speaking = False
        
    def process_speech(self):
        if self.is_speaking:
            return
            
        text = self.text_input.toPlainText().strip()
        if not text:
            return
            
        self.is_speaking = True
        self.speak_button.setEnabled(False)
        
        # Start speech in another thread
        threading.Thread(target=self.voice_generator.speak_text, args=(text,)).start()
    
    def on_phoneme(self, phoneme, duration):
        # Update 3D model animation based on phoneme
        self.avatar_view.update_face_for_phoneme(phoneme)
        
    def speech_finished(self, message):
        self.is_speaking = False
        self.speak_button.setEnabled(True)
        # Reset to rest position
        self.avatar_view.update_face_for_phoneme("rest")
    
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