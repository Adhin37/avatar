/**
 * Main Application Controller
 * Orchestrates all components: Avatar, TTS, Audio, and LipSync
 */

import { AvatarController } from './AvatarController.js';
import { TTSController } from './TTSController.js';
import { AudioPlayer } from './AudioPlayer.js';
import { LipSyncController } from './LipSyncController.js';

export class App {
    /**
     * Initialize the main application
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
        
        // Application state
        this.isInitialized = false;
        this.isSpeaking = false;
        this.currentSynthesis = null;
        
        // Bind methods to preserve context
        this.handleSpeak = this.handleSpeak.bind(this);
        this.handleStop = this.handleStop.bind(this);
        this.handleSpeedChange = this.handleSpeedChange.bind(this);
        this.handleVolumeChange = this.handleVolumeChange.bind(this);
        this.onSpeechEnd = this.onSpeechEnd.bind(this);
    }
    
    /**
     * Initialize the application and all components
     */
    async initialize() {
        try {
            this.setStatus('Initializing application...', 'connecting');
            
            // Get UI elements
            this.setupUI();
            
            // Initialize components in order
            await this.initializeComponents();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Check TTS server connectivity
            await this.checkTTSServer();
            
            this.isInitialized = true;
            this.setStatus('Ready to speak! Type your message and click Speak.', 'ready');
            this.hideLoadingOverlay();
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.hideLoadingOverlay();
        }
    }
    
    /**
     * Get references to UI elements
     */
    setupUI() {
        this.textInput = document.getElementById('text-input');
        this.speakBtn = document.getElementById('speak-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.speedSlider = document.getElementById('speed-slider');
        this.volumeSlider = document.getElementById('volume-slider');
        this.statusText = document.getElementById('status-text');
        
        // Validate all elements exist
        const elements = [
            this.textInput, this.speakBtn, this.stopBtn,
            this.speedSlider, this.volumeSlider, this.statusText
        ];
        
        if (elements.some(el => !el)) {
            throw new Error('Missing required UI elements');
        }
    }
    
    /**
     * Initialize all component controllers
     */
    async initializeComponents() {
        this.setStatus('Loading 3D avatar...', 'connecting');
        
        // Initialize Avatar Controller
        this.avatarController = new AvatarController('avatar-canvas');
        await this.avatarController.initialize();
        
        this.setStatus('Connecting to TTS server...', 'connecting');
        
        // Initialize TTS Controller
        this.ttsController = new TTSController('http://localhost:5000');
        
        this.setStatus('Initializing audio system...', 'connecting');
        
        // Initialize Audio Player
        this.audioPlayer = new AudioPlayer();
        await this.audioPlayer.initialize();
        
        this.setStatus('Setting up lip sync...', 'connecting');
        
        // Initialize Lip Sync Controller
        this.lipSyncController = new LipSyncController(
            this.avatarController,
            this.audioPlayer
        );
        await this.lipSyncController.initialize(this.ttsController);
    }
    
    /**
     * Setup event listeners for UI interactions
     */
    setupEventListeners() {
        // Speak button
        this.speakBtn.addEventListener('click', this.handleSpeak);
        
        // Stop button
        this.stopBtn.addEventListener('click', this.handleStop);
        
        // Speed slider
        this.speedSlider.addEventListener('input', this.handleSpeedChange);
        
        // Volume slider
        this.volumeSlider.addEventListener('input', this.handleVolumeChange);
        
        // Enter key in text input
        this.textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleSpeak();
            }
        });
        
        // Character counter for text input
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
     * Handle speak button click
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
            
            const speed = parseFloat(this.speedSlider.value);
            
            this.setStatus('Synthesizing speech...', 'speaking');
            
            // Synthesize speech
            const synthesis = await this.ttsController.synthesize(text, speed);
            this.currentSynthesis = synthesis;
            
            this.setStatus('Playing speech...', 'speaking');
            
            // Load audio
            await this.audioPlayer.loadBase64Audio(synthesis.audio_data);
            
            // Setup lip sync
            this.lipSyncController.loadTimings(synthesis.phoneme_timings);
            
            // Start playback and lip sync
            await this.audioPlayer.play(this.onSpeechEnd);
            this.lipSyncController.start();
            
            this.setStatus(`Speaking: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`, 'speaking');
            
        } catch (error) {
            console.error('Speech synthesis failed:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
            this.onSpeechEnd();
        }
    }
    
    /**
     * Handle stop button click
     */
    handleStop() {
        if (!this.isSpeaking) {
            return;
        }
        
        try {
            // Stop audio playback
            this.audioPlayer.stop();
            
            // Stop lip sync
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
        
        if (this.statusText.classList.contains('status-speaking')) {
            this.setStatus('Ready to speak! Type your message and click Speak.', 'ready');
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
     * @param {string} message - Status message
     * @param {string} type - Status type: 'connecting', 'ready', 'error', 'speaking'
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
     * Show error message in loading overlay
     * @param {string} message - Error message
     */
    showLoadingError(message) {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        if (overlay && loadingText) {
            loadingText.textContent = `Error: ${message}`;
            overlay.style.backgroundColor = 'rgba(244, 67, 54, 0.8)';
            
            // Hide spinner
            const spinner = overlay.querySelector('.loading-spinner');
            if (spinner) {
                spinner.style.display = 'none';
            }
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
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.cleanup();
    }
});
