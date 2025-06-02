/**
 * Enhanced Main Application Controller
 * Integrates realistic avatar with emotion system and advanced features
 */

import { EnhancedAvatarController } from './EnhancedAvatarController.js';
import { TTSController } from './TTSController.js';
import { AudioPlayer } from './AudioPlayer.js';
import { LipSyncController } from './LipSyncController.js';

export class EnhancedApp {
    /**
     * Initialize the enhanced application
     */
    constructor() {
        // Component controllers
        this.avatarController = null;
        this.ttsController = null;
        this.audioPlayer = null;
        this.lipSyncController = null;
        
        // UI elements
        this.textInput = null;
        this.speakBtn = null;
        this.stopBtn = null;
        this.speedSlider = null;
        this.volumeSlider = null;
        this.statusText = null;
        
        // Enhanced UI elements
        this.emotionControls = null;
        this.expressionSliders = {};
        this.eyeTrackingToggle = null;
        this.idleAnimationsToggle = null;
        this.contextSelector = null;
        
        // Application state
        this.isInitialized = false;
        this.isSpeaking = false;
        this.currentSynthesis = null;
        this.currentContext = 'neutral';
        
        // Emotion system
        this.emotionSystem = {
            enabled: true,
            autoDetect: true,
            intensity: 0.8,
            duration: 3000,
            currentEmotion: 'neutral'
        };
        
        // Eye tracking system
        this.eyeTracking = {
            enabled: false,
            sensitivity: 0.3,
            smoothing: 0.1,
            currentTarget: { x: 0, y: 0 },
            targetPosition: { x: 0, y: 0 }
        };
        
        // Context awareness
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
        
        // Bind methods to preserve context
        this.handleSpeak = this.handleSpeak.bind(this);
        this.handleStop = this.handleStop.bind(this);
        this.handleSpeedChange = this.handleSpeedChange.bind(this);
        this.handleVolumeChange = this.handleVolumeChange.bind(this);
        this.handleMouseMove = this.handleMouseMove.bind(this);
        this.handleExpressionChange = this.handleExpressionChange.bind(this);
        this.handleContextChange = this.handleContextChange.bind(this);
        this.onSpeechEnd = this.onSpeechEnd.bind(this);
        this.updateEyeTracking = this.updateEyeTracking.bind(this);
    }
    
    /**
     * Initialize the enhanced application
     */
    async initialize() {
        try {
            this.setStatus('Initializing enhanced avatar system...', 'connecting');
            
            // Get UI elements
            this.setupUI();
            this.setupEnhancedUI();
            
            // Initialize components in order
            await this.initializeComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            this.setupEnhancedEventListeners();
            
            // Check TTS server connectivity
            await this.checkTTSServer();
            
            // Initialize enhanced systems
            this.initializeEmotionSystem();
            this.initializeEyeTracking();
            this.initializeContextSystem();
            
            this.isInitialized = true;
            this.setStatus('Enhanced avatar ready! Try different emotions and contexts.', 'ready');
            this.hideLoadingOverlay();
            
        } catch (error) {
            console.error('Failed to initialize enhanced application:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.hideLoadingOverlay();
        }
    }
    
    /**
     * Get references to basic UI elements
     */
    setupUI() {
        this.textInput = document.getElementById('text-input');
        this.speakBtn = document.getElementById('speak-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.speedSlider = document.getElementById('speed-slider');
        this.volumeSlider = document.getElementById('volume-slider');
        this.statusText = document.getElementById('status-text');
        
        // Validate all basic elements exist
        const elements = [
            this.textInput, this.speakBtn, this.stopBtn,
            this.speedSlider, this.volumeSlider, this.statusText
        ];
        
        if (elements.some(el => !el)) {
            throw new Error('Missing required UI elements');
        }
    }
    
    /**
     * Setup enhanced UI elements
     */
    setupEnhancedUI() {
        this.createEnhancedControls();
    }
    
    /**
     * Create enhanced control panel
     */
    createEnhancedControls() {
        const controlsSection = document.querySelector('.controls-section');
        if (!controlsSection) return;
        
        // Create enhanced controls container
        const enhancedControls = document.createElement('div');
        enhancedControls.className = 'enhanced-controls';
        enhancedControls.innerHTML = `
            <div class="control-group">
                <label>Context:</label>
                <select id="context-selector">
                    <option value="neutral">Neutral</option>
                    <option value="greeting">Greeting</option>
                    <option value="farewell">Farewell</option>
                    <option value="question">Question</option>
                    <option value="explanation">Explanation</option>
                    <option value="error">Error</option>
                    <option value="success">Success</option>
                    <option value="thinking">Thinking</option>
                    <option value="confused">Confused</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Quick Emotions:</label>
                <div class="emotion-buttons">
                    <button class="emotion-btn" data-emotion="happy">😊 Happy</button>
                    <button class="emotion-btn" data-emotion="sad">😢 Sad</button>
                    <button class="emotion-btn" data-emotion="surprised">😲 Surprised</button>
                    <button class="emotion-btn" data-emotion="angry">😠 Angry</button>
                    <button class="emotion-btn" data-emotion="neutral">😐 Neutral</button>
                </div>
            </div>
            
            <div class="control-group">
                <label>Eye Tracking:</label>
                <div class="toggle-container">
                    <input type="checkbox" id="eye-tracking-toggle">
                    <label for="eye-tracking-toggle">Mouse Eye Tracking</label>
                </div>
            </div>
            
            <div class="control-group">
                <label>Idle Animations:</label>
                <div class="toggle-container">
                    <input type="checkbox" id="idle-animations-toggle" checked>
                    <label for="idle-animations-toggle">Natural Movements</label>
                </div>
            </div>
            
            <div class="control-group">
                <label>Expression Intensity:</label>
                <div class="slider-container">
                    <input type="range" id="emotion-intensity" min="0" max="1" step="0.1" value="0.8">
                    <span id="emotion-intensity-value">80%</span>
                </div>
            </div>
        `;
        
        // Add enhanced controls before button group
        const buttonGroup = controlsSection.querySelector('.button-group');
        controlsSection.insertBefore(enhancedControls, buttonGroup);
        
        // Get references to new elements
        this.contextSelector = document.getElementById('context-selector');
        this.eyeTrackingToggle = document.getElementById('eye-tracking-toggle');
        this.idleAnimationsToggle = document.getElementById('idle-animations-toggle');
        this.emotionIntensitySlider = document.getElementById('emotion-intensity');
        
        // Add styles for enhanced controls
        this.addEnhancedStyles();
    }
    
    /**
     * Add CSS styles for enhanced controls
     */
    addEnhancedStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .enhanced-controls {
                display: flex;
                flex-direction: column;
                gap: 15px;
                padding: 15px 0;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                margin-top: 15px;
            }
            
            .emotion-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
            
            .emotion-btn {
                padding: 8px 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
            }
            
            .emotion-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-1px);
            }
            
            .emotion-btn.active {
                background: rgba(76, 175, 80, 0.3);
                box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
            }
            
            .toggle-container {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .toggle-container input[type="checkbox"] {
                width: 16px;
                height: 16px;
                accent-color: #4caf50;
            }
            
            .toggle-container label {
                font-size: 14px;
                cursor: pointer;
            }
            
            #context-selector {
                width: 100%;
                padding: 8px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 14px;
            }
            
            #emotion-intensity-value {
                min-width: 40px;
                text-align: center;
                font-size: 12px;
                background: rgba(255, 255, 255, 0.2);
                padding: 2px 6px;
                border-radius: 10px;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Initialize all component controllers
     */
    async initializeComponents() {
        this.setStatus('Loading enhanced 3D avatar...', 'connecting');
        
        // Initialize Enhanced Avatar Controller
        this.avatarController = new EnhancedAvatarController('avatar-canvas');
        await this.avatarController.initialize();
        
        this.setStatus('Connecting to TTS server...', 'connecting');
        
        // Initialize TTS Controller
        this.ttsController = new TTSController('http://localhost:5000');
        
        this.setStatus('Initializing enhanced audio system...', 'connecting');
        
        // Initialize Audio Player
        this.audioPlayer = new AudioPlayer();
        await this.audioPlayer.initialize();
        
        this.setStatus('Setting up advanced lip sync...', 'connecting');
        
        // Initialize Lip Sync Controller
        this.lipSyncController = new LipSyncController(
            this.avatarController,
            this.audioPlayer
        );
        await this.lipSyncController.initialize(this.ttsController);
    }
    
    /**
     * Setup basic event listeners
     */
    setupEventListeners() {
        // Basic controls
        this.speakBtn.addEventListener('click', this.handleSpeak);
        this.stopBtn.addEventListener('click', this.handleStop);
        this.speedSlider.addEventListener('input', this.handleSpeedChange);
        this.volumeSlider.addEventListener('input', this.handleVolumeChange);
        
        // Keyboard shortcuts
        this.textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleSpeak();
            }
        });
        
        // Character counter
        this.textInput.addEventListener('input', () => {
            const remaining = 1000 - this.textInput.value.length;
            if (remaining < 100) {
                this.textInput.style.borderColor = remaining < 0 ? '#f44336' : '#ff9800';
            } else {
                this.textInput.style.borderColor = '';
            }
        });
    }
    
    /**
     * Setup enhanced event listeners
     */
    setupEnhancedEventListeners() {
        // Emotion buttons
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const emotion = btn.getAttribute('data-emotion');
                this.triggerEmotion(emotion);
                this.updateEmotionButtonStates(emotion);
            });
        });
        
        // Context selector
        if (this.contextSelector) {
            this.contextSelector.addEventListener('change', this.handleContextChange);
        }
        
        // Eye tracking toggle
        if (this.eyeTrackingToggle) {
            this.eyeTrackingToggle.addEventListener('change', (e) => {
                this.setEyeTracking(e.target.checked);
            });
        }
        
        // Idle animations toggle
        if (this.idleAnimationsToggle) {
            this.idleAnimationsToggle.addEventListener('change', (e) => {
                this.avatarController.setIdleAnimationsEnabled(e.target.checked);
            });
        }
        
        // Emotion intensity slider
        if (this.emotionIntensitySlider) {
            this.emotionIntensitySlider.addEventListener('input', (e) => {
                this.emotionSystem.intensity = parseFloat(e.target.value);
                document.getElementById('emotion-intensity-value').textContent = 
                    Math.round(this.emotionSystem.intensity * 100) + '%';
            });
        }
        
        // Mouse movement for eye tracking
        const canvas = document.getElementById('avatar-canvas');
        if (canvas) {
            canvas.addEventListener('mousemove', this.handleMouseMove);
            canvas.addEventListener('mouseleave', () => {
                if (this.eyeTracking.enabled) {
                    this.avatarController.setEyeLookDirection(0, 0);
                }
            });
        }
        
        // Start eye tracking update loop
        this.startEyeTrackingUpdate();
    }
    
    /**
     * Initialize emotion system
     */
    initializeEmotionSystem() {
        console.log('Initializing emotion system');
        this.emotionSystem.currentEmotion = 'neutral';
        this.avatarController.setExpression('neutral', 1.0);
    }
    
    /**
     * Initialize eye tracking system
     */
    initializeEyeTracking() {
        console.log('Initializing eye tracking system');
        this.eyeTracking.enabled = false;
    }
    
    /**
     * Initialize context awareness system
     */
    initializeContextSystem() {
        console.log('Initializing context system');
        this.contextSystem.currentContext = 'neutral';
    }
    
    /**
     * Check if TTS server is available
     */
    async checkTTSServer() {
        try {
            await this.ttsController.checkHealth();
        } catch (error) {
            throw new Error('TTS server not available. Please start the Python server first.');
        }
    }
    
    /**
     * Handle speak button click with enhanced features
     */
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
            
            // Analyze text and set context
            this.analyzeAndSetContext(text);
            
            // Apply context-based emotions
            this.applyContextEmotion();
            
            const speed = parseFloat(this.speedSlider.value);
            
            this.setStatus('Synthesizing speech...', 'speaking');
            
            // Synthesize speech
            const synthesis = await this.ttsController.synthesize(text, speed);
            this.currentSynthesis = synthesis;
            
            this.setStatus('Playing speech with enhanced expressions...', 'speaking');
            
            // Load audio
            await this.audioPlayer.loadBase64Audio(synthesis.audio_data);
            
            // Setup lip sync
            this.lipSyncController.loadTimings(synthesis.phoneme_timings);
            
            // Start playback and lip sync
            await this.audioPlayer.play(this.onSpeechEnd);
            this.lipSyncController.start();
            
            this.setStatus(`Speaking: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`, 'speaking');
            
        } catch (error) {
            console.error('Enhanced speech synthesis failed:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.onSpeechEnd();
        }
    }
    
    /**
     * Analyze text and determine appropriate context
     */
    analyzeAndSetContext(text) {
        const lowercaseText = text.toLowerCase();
        
        // Simple keyword-based context detection
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
        
        // Update context if auto-detection is enabled
        if (this.contextSystem.enabled && maxMatches > 0) {
            this.setContext(detectedContext);
        }
    }
    
    /**
     * Set current context
     */
    setContext(context) {
        this.contextSystem.currentContext = context;
        this.contextSystem.contextHistory.push({
            context: context,
            timestamp: Date.now()
        });
        
        // Update UI
        if (this.contextSelector) {
            this.contextSelector.value = context;
        }
        
        console.log(`Context set to: ${context}`);
    }
    
    /**
     * Apply emotion based on current context
     */
    applyContextEmotion() {
        const emotion = this.contextSystem.emotionMapping[this.contextSystem.currentContext];
        
        if (emotion && this.emotionSystem.enabled) {
            this.triggerEmotion(emotion, this.emotionSystem.intensity);
        }
    }
    
    /**
     * Trigger an emotion with specified intensity
     */
    triggerEmotion(emotion, intensity = null) {
        const emotionIntensity = intensity || this.emotionSystem.intensity;
        
        this.emotionSystem.currentEmotion = emotion;
        this.avatarController.triggerExpression(emotion, emotionIntensity, this.emotionSystem.duration);
        
        console.log(`Triggered emotion: ${emotion} at ${Math.round(emotionIntensity * 100)}%`);
    }
    
    /**
     * Update emotion button visual states
     */
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
    
    /**
     * Handle context selection change
     */
    handleContextChange() {
        const selectedContext = this.contextSelector.value;
        this.setContext(selectedContext);
        this.applyContextEmotion();
    }
    
    /**
     * Set eye tracking enabled/disabled
     */
    setEyeTracking(enabled) {
        this.eyeTracking.enabled = enabled;
        
        if (!enabled) {
            // Return eyes to center
            this.avatarController.setEyeLookDirection(0, 0);
        }
        
        console.log(`Eye tracking: ${enabled ? 'enabled' : 'disabled'}`);
    }
    
    /**
     * Handle mouse movement for eye tracking
     */
    handleMouseMove(event) {
        if (!this.eyeTracking.enabled) return;
        
        const canvas = event.target;
        const rect = canvas.getBoundingClientRect();
        
        // Convert mouse position to normalized coordinates (-1 to 1)
        const x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
        const y = ((event.clientY - rect.top) / rect.height - 0.5) * -2;
        
        // Apply sensitivity and bounds
        this.eyeTracking.targetPosition.x = Math.max(-1, Math.min(1, x * this.eyeTracking.sensitivity));
        this.eyeTracking.targetPosition.y = Math.max(-1, Math.min(1, y * this.eyeTracking.sensitivity));
    }
    
    /**
     * Start eye tracking update loop
     */
    startEyeTrackingUpdate() {
        const updateEyeTracking = () => {
            if (this.eyeTracking.enabled) {
                // Smooth interpolation to target position
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
    
    /**
     * Handle stop button click
     */
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
    
    /**
     * Handle speech speed slider change
     */
    handleSpeedChange() {
        const speed = parseFloat(this.speedSlider.value);
        document.getElementById('speed-value').textContent = `${speed.toFixed(1)}x`;
    }
    
    /**
     * Handle volume slider change
     */
    handleVolumeChange() {
        const volume = parseInt(this.volumeSlider.value);
        document.getElementById('volume-value').textContent = `${volume}%`;
        
        if (this.audioPlayer) {
            this.audioPlayer.setVolume(volume / 100);
        }
    }
    
    /**
     * Called when speech playback ends
     */
    onSpeechEnd() {
        this.isSpeaking = false;
        this.currentSynthesis = null;
        this.updateButtonStates();
        
        // Stop lip sync
        if (this.lipSyncController) {
            this.lipSyncController.stop();
        }
        
        // Return to neutral expression after a delay
        setTimeout(() => {
            if (!this.isSpeaking) {
                this.triggerEmotion('neutral', 1.0);
                this.updateEmotionButtonStates('neutral');
            }
        }, 2000);
        
        if (this.statusText.classList.contains('status-speaking')) {
            this.setStatus('Ready for enhanced avatar interaction!', 'ready');
        }
    }
    
    /**
     * Update button enabled/disabled states
     */
    updateButtonStates() {
        this.speakBtn.disabled = this.isSpeaking;
        this.stopBtn.disabled = !this.isSpeaking;
        
        // Update button text
        if (this.isSpeaking) {
            this.speakBtn.innerHTML = '⏳ Speaking...';
        } else {
            this.speakBtn.innerHTML = '🎤 Speak';
        }
    }
    
    /**
     * Set status message and styling
     */
    setStatus(message, type) {
        if (!this.statusText) return;
        
        this.statusText.textContent = message;
        
        // Remove all status classes
        this.statusText.classList.remove('status-connecting', 'status-ready', 'status-error', 'status-speaking');
        
        // Add current status class
        this.statusText.classList.add(`status-${type}`);
        
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    /**
     * Hide the loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    /**
     * Cleanup resources when page unloads
     */
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
    
    /**
     * Get current system status
     */
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
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.enhancedApp) {
        window.enhancedApp.cleanup();
    }
});
