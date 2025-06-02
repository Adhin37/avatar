/**
 * Main Application Controller
 * Orchestrates avatar, TTS, audio, and lip sync with facial expressions and emotion system
 */

import { AvatarController } from './AvatarController.js';
import { TTSController } from './TTSController.js';
import { AudioPlayer } from './AudioPlayer.js';
import { LipSyncController } from './LipSyncController.js';
import { EmotionAnalyzer } from './EmotionAnalyzer.js';

export class App {
    constructor() {
        this.avatarController = null;
        this.ttsController = null;
        this.audioPlayer = null;
        this.lipSyncController = null;
        this.emotionAnalyzer = null;
        
        this.textInput = null;
        this.speakBtn = null;
        this.stopBtn = null;
        this.speedSlider = null;
        this.volumeSlider = null;
        this.statusText = null;
        this.emotionControls = null;
        this.contextSelector = null;
        this.eyeTrackingToggle = null;
        this.idleAnimationsToggle = null;
        this.emotionIntensitySlider = null;
        
        this.isInitialized = false;
        this.isSpeaking = false;
        this.currentSynthesis = null;
        this.currentContext = 'neutral';
        
        this.emotionSystem = {
            enabled: true,
            autoDetect: true,
            intensity: 0.8,
            duration: 3000,
            currentEmotion: 'neutral'
        };
        
        this.eyeTracking = {
            enabled: false,
            sensitivity: 0.3,
            smoothing: 0.1,
            currentTarget: { x: 0, y: 0 },
            targetPosition: { x: 0, y: 0 }
        };
        
        this.contextSystem = {
            enabled: true,
            currentContext: 'neutral',
            contextHistory: [],
            emotionMapping: {
                'greeting': 'happy',
                'farewell': 'sad',
                'question': 'surprised',
                'explanation': 'neutral',
                'error': 'sad',
                'success': 'happy',
                'thinking': 'neutral',
                'confused': 'surprised'
            }
        };
        
        this.handleSpeak = this.handleSpeak.bind(this);
        this.handleStop = this.handleStop.bind(this);
        this.handleSpeedChange = this.handleSpeedChange.bind(this);
        this.handleVolumeChange = this.handleVolumeChange.bind(this);
        this.handleMouseMove = this.handleMouseMove.bind(this);
        this.handleContextChange = this.handleContextChange.bind(this);
        this.onSpeechEnd = this.onSpeechEnd.bind(this);
        this.updateEyeTracking = this.updateEyeTracking.bind(this);
    }
    
    async initialize() {
        try {
            this.setStatus('Initializing avatar system...', 'connecting');
            
            this.setupUI();
            await this.initializeComponents();
            this.setupEventListeners();
            await this.checkTTSServer();
            this.initializeFeatureSystems();
            
            this.isInitialized = true;
            this.setStatus('Avatar ready! Try different emotions and contexts.', 'ready');
            this.hideLoadingOverlay();
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.hideLoadingOverlay();
        }
    }
    
    setupUI() {
        this.textInput = document.getElementById('text-input');
        this.speakBtn = document.getElementById('speak-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.speedSlider = document.getElementById('speed-slider');
        this.volumeSlider = document.getElementById('volume-slider');
        this.statusText = document.getElementById('status-text');
        this.contextSelector = document.getElementById('context-selector');
        this.eyeTrackingToggle = document.getElementById('eye-tracking-toggle');
        this.idleAnimationsToggle = document.getElementById('idle-animations-toggle');
        this.emotionIntensitySlider = document.getElementById('emotion-intensity');
        
        const elements = [
            this.textInput, this.speakBtn, this.stopBtn,
            this.speedSlider, this.volumeSlider, this.statusText
        ];
        
        if (elements.some(el => !el)) {
            throw new Error('Missing required UI elements');
        }
    }
    
    async initializeComponents() {
        this.setStatus('Loading 3D avatar...', 'connecting');
        
        this.avatarController = new AvatarController('avatar-canvas');
        await this.avatarController.initialize();
        
        this.setStatus('Connecting to TTS server...', 'connecting');
        
        this.ttsController = new TTSController('http://localhost:5000');
        
        this.setStatus('Initializing audio system...', 'connecting');
        
        this.audioPlayer = new AudioPlayer();
        await this.audioPlayer.initialize();
        
        this.setStatus('Setting up lip sync...', 'connecting');
        
        this.lipSyncController = new LipSyncController(
            this.avatarController,
            this.audioPlayer
        );
        await this.lipSyncController.initialize(this.ttsController);
        
        this.emotionAnalyzer = new EmotionAnalyzer();
    }
    
    setupEventListeners() {
        this.speakBtn.addEventListener('click', this.handleSpeak);
        this.stopBtn.addEventListener('click', this.handleStop);
        this.speedSlider.addEventListener('input', this.handleSpeedChange);
        this.volumeSlider.addEventListener('input', this.handleVolumeChange);
        
        this.textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleSpeak();
            }
        });
        
        this.textInput.addEventListener('input', () => {
            const count = this.textInput.value.length;
            const charCount = document.getElementById('char-count');
            if (charCount) {
                charCount.textContent = count;
                if (count > 900) {
                    charCount.style.color = '#f44336';
                } else if (count > 700) {
                    charCount.style.color = '#ff9800';
                } else {
                    charCount.style.color = '';
                }
            }
        });
        
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const emotion = btn.getAttribute('data-emotion');
                this.triggerEmotion(emotion);
                this.updateEmotionButtonStates(emotion);
            });
        });
        
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.getAttribute('data-text');
                const context = btn.getAttribute('data-context');
                
                this.textInput.value = text;
                
                if (context && this.contextSelector) {
                    this.contextSelector.value = context;
                    this.contextSelector.dispatchEvent(new Event('change'));
                }
                
                const charCount = document.getElementById('char-count');
                if (charCount) {
                    charCount.textContent = text.length;
                }
                
                if (!this.isSpeaking) {
                    setTimeout(() => {
                        this.speakBtn.click();
                    }, 500);
                }
            });
        });
        
        if (this.contextSelector) {
            this.contextSelector.addEventListener('change', this.handleContextChange);
        }
        
        if (this.eyeTrackingToggle) {
            this.eyeTrackingToggle.addEventListener('change', (e) => {
                this.setEyeTracking(e.target.checked);
            });
        }
        
        if (this.idleAnimationsToggle) {
            this.idleAnimationsToggle.addEventListener('change', (e) => {
                this.avatarController.setIdleAnimationsEnabled(e.target.checked);
            });
        }
        
        if (this.emotionIntensitySlider) {
            this.emotionIntensitySlider.addEventListener('input', (e) => {
                this.emotionSystem.intensity = parseFloat(e.target.value);
                const valueDisplay = document.getElementById('emotion-intensity-value');
                if (valueDisplay) {
                    valueDisplay.textContent = Math.round(this.emotionSystem.intensity * 100) + '%';
                }
            });
        }
        
        const canvas = document.getElementById('avatar-canvas');
        if (canvas) {
            canvas.addEventListener('mousemove', this.handleMouseMove);
            canvas.addEventListener('mouseleave', () => {
                if (this.eyeTracking.enabled) {
                    this.avatarController.setEyeLookDirection(0, 0);
                }
            });
        }
        
        const debugToggle = document.getElementById('debug-mode-toggle');
        if (debugToggle) {
            debugToggle.addEventListener('change', (e) => {
                const debugPanel = document.getElementById('expression-debug');
                if (debugPanel) {
                    debugPanel.style.display = e.target.checked ? 'block' : 'none';
                }
            });
        }
        
        const autoEmotionToggle = document.getElementById('auto-emotion-toggle');
        if (autoEmotionToggle) {
            autoEmotionToggle.addEventListener('change', (e) => {
                this.emotionSystem.autoDetect = e.target.checked;
            });
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '6' && !e.ctrlKey && !e.altKey) {
                const emotions = ['neutral', 'happy', 'sad', 'surprised', 'angry', 'fearful'];
                const emotionIndex = parseInt(e.key) - 1;
                
                if (emotionIndex < emotions.length) {
                    const emotionBtn = document.querySelector(`[data-emotion="${emotions[emotionIndex]}"]`);
                    if (emotionBtn) {
                        emotionBtn.click();
                    }
                }
            }
        });
        
        this.startEyeTrackingUpdate();
    }
    
    initializeFeatureSystems() {
        console.log('Initializing feature systems');
        this.emotionSystem.currentEmotion = 'neutral';
        this.avatarController.setExpression('neutral', 1.0);
        this.eyeTracking.enabled = false;
        this.contextSystem.currentContext = 'neutral';
    }
    
    async checkTTSServer() {
        try {
            await this.ttsController.checkHealth();
        } catch (error) {
            throw new Error('TTS server not available. Please start the Python server first.');
        }
    }
    
    async handleSpeak() {
        if (!this.isInitialized || this.isSpeaking) {
            return;
        }
        
        const text = this.textInput.value.trim();
        if (!text) {
            this.setStatus('Please enter some text to speak.', 'error');
            return;
        }
        
        if (text.length > 1000) {
            this.setStatus('Text too long. Maximum 1000 characters.', 'error');
            return;
        }
        
        try {
            this.isSpeaking = true;
            this.updateButtonStates();
            
            this.analyzeAndSetContext(text);
            this.applyContextEmotion();
            
            const speed = parseFloat(this.speedSlider.value);
            
            this.setStatus('Synthesizing speech...', 'speaking');
            
            const synthesis = await this.ttsController.synthesize(text, speed);
            this.currentSynthesis = synthesis;
            
            this.setStatus('Playing speech with expressions...', 'speaking');
            
            await this.audioPlayer.loadBase64Audio(synthesis.audio_data);
            this.lipSyncController.loadTimings(synthesis.phoneme_timings);
            
            await this.audioPlayer.play(this.onSpeechEnd);
            this.lipSyncController.start();
            
            this.setStatus(`Speaking: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`, 'speaking');
            
        } catch (error) {
            console.error('Speech synthesis failed:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.onSpeechEnd();
        }
    }
    
    analyzeAndSetContext(text) {
        if (this.emotionSystem.autoDetect && this.emotionAnalyzer) {
            const analysis = this.emotionAnalyzer.analyze(text);
            
            if (analysis.confidence > 0.5) {
                this.triggerEmotion(analysis.primaryEmotion, analysis.intensity);
            }
            
            if (analysis.context !== 'neutral') {
                this.setContext(analysis.context);
            }
        } else {
            const lowercaseText = text.toLowerCase();
            
            const contextKeywords = {
                'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'welcome'],
                'farewell': ['goodbye', 'bye', 'see you', 'farewell', 'until next time', 'take care'],
                'question': ['what', 'why', 'how', 'when', 'where', 'who', 'which', '?'],
                'error': ['error', 'problem', 'issue', 'wrong', 'failed', 'cannot', 'unable', 'sorry'],
                'success': ['great', 'excellent', 'perfect', 'wonderful', 'success', 'completed', 'done'],
                'thinking': ['hmm', 'let me think', 'considering', 'perhaps', 'maybe', 'possibly'],
                'confused': ['confused', 'unclear', 'not sure', 'uncertain', 'puzzled', 'bewildered']
            };
            
            let detectedContext = 'neutral';
            let maxMatches = 0;
            
            Object.keys(contextKeywords).forEach(context => {
                const keywords = contextKeywords[context];
                const matches = keywords.filter(keyword => lowercaseText.includes(keyword)).length;
                
                if (matches > maxMatches) {
                    maxMatches = matches;
                    detectedContext = context;
                }
            });
            
            if (this.contextSystem.enabled && maxMatches > 0) {
                this.setContext(detectedContext);
            }
        }
    }
    
    setContext(context) {
        this.contextSystem.currentContext = context;
        this.contextSystem.contextHistory.push({
            context: context,
            timestamp: Date.now()
        });
        
        if (this.contextSelector) {
            this.contextSelector.value = context;
        }
        
        const currentContextEl = document.getElementById('current-context');
        if (currentContextEl) {
            currentContextEl.textContent = context;
        }
        
        console.log(`Context set to: ${context}`);
    }
    
    applyContextEmotion() {
        const emotion = this.contextSystem.emotionMapping[this.contextSystem.currentContext];
        
        if (emotion && this.emotionSystem.enabled) {
            this.triggerEmotion(emotion, this.emotionSystem.intensity);
        }
    }
    
    triggerEmotion(emotion, intensity = null) {
        const emotionIntensity = intensity || this.emotionSystem.intensity;
        
        this.emotionSystem.currentEmotion = emotion;
        this.avatarController.triggerExpression(emotion, emotionIntensity, this.emotionSystem.duration);
        
        const currentEmotionEl = document.getElementById('current-emotion');
        if (currentEmotionEl) {
            currentEmotionEl.textContent = emotion;
        }
        
        console.log(`Triggered emotion: ${emotion} at ${Math.round(emotionIntensity * 100)}%`);
    }
    
    updateEmotionButtonStates(activeEmotion) {
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            const emotion = btn.getAttribute('data-emotion');
            if (emotion === activeEmotion) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
    
    handleContextChange() {
        if (!this.contextSelector) return;
        
        const selectedContext = this.contextSelector.value;
        this.setContext(selectedContext);
        this.applyContextEmotion();
    }
    
    setEyeTracking(enabled) {
        this.eyeTracking.enabled = enabled;
        
        if (!enabled) {
            this.avatarController.setEyeLookDirection(0, 0);
        }
        
        console.log(`Eye tracking: ${enabled ? 'enabled' : 'disabled'}`);
    }
    
    handleMouseMove(event) {
        if (!this.eyeTracking.enabled) return;
        
        const canvas = event.target;
        const rect = canvas.getBoundingClientRect();
        
        const x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
        const y = ((event.clientY - rect.top) / rect.height - 0.5) * -2;
        
        this.eyeTracking.targetPosition.x = Math.max(-1, Math.min(1, x * this.eyeTracking.sensitivity));
        this.eyeTracking.targetPosition.y = Math.max(-1, Math.min(1, y * this.eyeTracking.sensitivity));
    }
    
    startEyeTrackingUpdate() {
        const updateEyeTracking = () => {
            if (this.eyeTracking.enabled) {
                const smoothing = this.eyeTracking.smoothing;
                
                this.eyeTracking.currentTarget.x += 
                    (this.eyeTracking.targetPosition.x - this.eyeTracking.currentTarget.x) * smoothing;
                this.eyeTracking.currentTarget.y += 
                    (this.eyeTracking.targetPosition.y - this.eyeTracking.currentTarget.y) * smoothing;
                
                this.avatarController.setEyeLookDirection(
                    this.eyeTracking.currentTarget.x,
                    this.eyeTracking.currentTarget.y
                );
            }
            
            requestAnimationFrame(updateEyeTracking);
        };
        
        updateEyeTracking();
    }
    
    handleStop() {
        if (!this.isSpeaking) return;
        
        try {
            this.audioPlayer.stop();
            this.lipSyncController.stop();
            this.onSpeechEnd();
            this.setStatus('Speech stopped.', 'ready');
        } catch (error) {
            console.error('Failed to stop speech:', error);
            this.setStatus(`Error stopping: ${error.message}`, 'error');
        }
    }
    
    handleSpeedChange() {
        const speed = parseFloat(this.speedSlider.value);
        const speedValue = document.getElementById('speed-value');
        if (speedValue) {
            speedValue.textContent = `${speed.toFixed(1)}x`;
        }
    }
    
    handleVolumeChange() {
        const volume = parseInt(this.volumeSlider.value);
        const volumeValue = document.getElementById('volume-value');
        if (volumeValue) {
            volumeValue.textContent = `${volume}%`;
        }
        
        if (this.audioPlayer) {
            this.audioPlayer.setVolume(volume / 100);
        }
    }
    
    onSpeechEnd() {
        this.isSpeaking = false;
        this.currentSynthesis = null;
        this.updateButtonStates();
        
        if (this.lipSyncController) {
            this.lipSyncController.stop();
        }
        
        setTimeout(() => {
            if (!this.isSpeaking) {
                this.triggerEmotion('neutral', 1.0);
                this.updateEmotionButtonStates('neutral');
            }
        }, 2000);
        
        if (this.statusText && this.statusText.classList.contains('status-speaking')) {
            this.setStatus('Ready for avatar interaction!', 'ready');
        }
    }
    
    updateButtonStates() {
        this.speakBtn.disabled = this.isSpeaking;
        this.stopBtn.disabled = !this.isSpeaking;
        
        if (this.isSpeaking) {
            this.speakBtn.innerHTML = '⏳ Speaking...';
        } else {
            this.speakBtn.innerHTML = '🎤 Speak';
        }
    }
    
    setStatus(message, type) {
        if (!this.statusText) return;
        
        this.statusText.textContent = message;
        
        this.statusText.classList.remove('status-connecting', 'status-ready', 'status-error', 'status-speaking');
        this.statusText.classList.add(`status-${type}`);
        
        const statusIndicators = {
            'connecting': { tts: '⏳', avatar: '⏳', emotion: '⏳' },
            'ready': { tts: '✅', avatar: '✅', emotion: '✅' },
            'error': { tts: '❌', avatar: '❌', emotion: '❌' },
            'speaking': { tts: '🔊', avatar: '🎭', emotion: '😊' }
        };
        
        const indicators = statusIndicators[type];
        if (indicators) {
            const ttsStatus = document.getElementById('tts-status');
            const avatarStatus = document.getElementById('avatar-status');
            const emotionStatus = document.getElementById('emotion-status');
            
            if (ttsStatus) ttsStatus.textContent = `TTS: ${indicators.tts}`;
            if (avatarStatus) avatarStatus.textContent = `Avatar: ${indicators.avatar}`;
            if (emotionStatus) emotionStatus.textContent = `Emotions: ${indicators.emotion}`;
        }
        
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    getSystemStatus() {
        return {
            initialized: this.isInitialized,
            speaking: this.isSpeaking,
            currentEmotion: this.emotionSystem.currentEmotion,
            currentContext: this.contextSystem.currentContext,
            eyeTrackingEnabled: this.eyeTracking.enabled,
            expressionStates: this.avatarController ? this.avatarController.getExpressionStates() : {}
        };
    }
    
    cleanup() {
        if (this.audioPlayer) {
            this.audioPlayer.cleanup();
        }
        
        if (this.avatarController) {
            this.avatarController.cleanup();
        }
        
        if (this.lipSyncController) {
            this.lipSyncController.cleanup();
        }
    }
}

window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.cleanup();
    }
});