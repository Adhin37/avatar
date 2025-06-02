/**
 * Audio Player
 * Handles audio decoding, playback, and timing queries using Web Audio API
 */

export class AudioPlayer {
    /**
     * Initialize the Audio Player
     */
    constructor() {
        // Web Audio API components
        this.audioContext = null;
        this.audioBuffer = null;
        this.sourceNode = null;
        this.gainNode = null;
        
        // Playback state
        this.isPlaying = false;
        this.isPaused = false;
        this.startTime = 0;
        this.pauseTime = 0;
        this.volume = 0.8;
        
        // Callbacks
        this.onEndedCallback = null;
        
        // Bind methods
        this.handleEnded = this.handleEnded.bind(this);
    }
    
    /**
     * Initialize the Web Audio API context
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create gain node for volume control
            this.gainNode = this.audioContext.createGain();
            this.gainNode.connect(this.audioContext.destination);
            this.gainNode.gain.value = this.volume;
            
            // Resume context if it's suspended (required for Chrome autoplay policy)
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            console.log('Audio Player initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize Audio Player:', error);
            throw new Error(`Audio initialization failed: ${error.message}`);
        }
    }
    
    /**
     * Load and decode base64 encoded audio data
     * @param {string} base64Data - Base64 encoded audio data
     * @returns {Promise<void>}
     */
    async loadBase64Audio(base64Data) {
        if (!this.audioContext) {
            throw new Error('Audio context not initialized');
        }
        
        if (!base64Data || typeof base64Data !== 'string') {
            throw new Error('Invalid base64 audio data');
        }
        
        try {
            // Convert base64 to ArrayBuffer
            const binaryString = atob(base64Data);
            const arrayBuffer = new ArrayBuffer(binaryString.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < binaryString.length; i++) {
                uint8Array[i] = binaryString.charCodeAt(i);
            }
            
            // Decode audio data
            this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            console.log('Audio loaded successfully:', {
                duration: this.audioBuffer.duration,
                sampleRate: this.audioBuffer.sampleRate,
                channels: this.audioBuffer.numberOfChannels
            });
            
        } catch (error) {
            console.error('Failed to load audio:', error);
            throw new Error(`Audio loading failed: ${error.message}`);
        }
    }
    
    /**
     * Load audio from a URL
     * @param {string} url - Audio file URL
     * @returns {Promise<void>}
     */
    async loadAudioFromUrl(url) {
        if (!this.audioContext) {
            throw new Error('Audio context not initialized');
        }
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to fetch audio: ${response.status}`);
            }
            
            const arrayBuffer = await response.arrayBuffer();
            this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            console.log('Audio loaded from URL:', url);
            
        } catch (error) {
            console.error('Failed to load audio from URL:', error);
            throw new Error(`Audio URL loading failed: ${error.message}`);
        }
    }
    
    /**
     * Play the loaded audio
     * @param {Function} onEndedCallback - Callback function to call when playback ends
     * @returns {Promise<void>}
     */
    async play(onEndedCallback = null) {
        if (!this.audioBuffer) {
            throw new Error('No audio loaded');
        }
        
        if (this.isPlaying) {
            console.warn('Audio is already playing');
            return;
        }
        
        try {
            // Resume audio context if suspended
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // Create new source node
            this.sourceNode = this.audioContext.createBufferSource();
            this.sourceNode.buffer = this.audioBuffer;
            this.sourceNode.connect(this.gainNode);
            
            // Set up ended callback
            this.onEndedCallback = onEndedCallback;
            this.sourceNode.onended = this.handleEnded;
            
            // Start playback
            this.sourceNode.start(0);
            this.startTime = this.audioContext.currentTime;
            this.isPlaying = true;
            this.isPaused = false;
            
            console.log('Audio playback started');
            
        } catch (error) {
            console.error('Failed to play audio:', error);
            throw new Error(`Audio playback failed: ${error.message}`);
        }
    }
    
    /**
     * Stop audio playback
     */
    stop() {
        if (!this.isPlaying) {
            return;
        }
        
        try {
            if (this.sourceNode) {
                this.sourceNode.stop();
                this.sourceNode.disconnect();
                this.sourceNode = null;
            }
            
            this.isPlaying = false;
            this.isPaused = false;
            this.startTime = 0;
            this.pauseTime = 0;
            
            console.log('Audio playback stopped');
            
        } catch (error) {
            console.error('Failed to stop audio:', error);
        }
    }
    
    /**
     * Pause audio playback (Note: Web Audio API doesn't support pause/resume directly)
     * This implementation stops the audio and remembers the position
     */
    pause() {
        if (!this.isPlaying || this.isPaused) {
            return;
        }
        
        this.pauseTime = this.getCurrentTimeMs() / 1000;
        this.stop();
        this.isPaused = true;
        
        console.log('Audio paused at:', this.pauseTime);
    }
    
    /**
     * Resume audio playback from paused position
     * @returns {Promise<void>}
     */
    async resume() {
        if (!this.isPaused || !this.audioBuffer) {
            return;
        }
        
        try {
            // Create new source node for resumed playback
            this.sourceNode = this.audioContext.createBufferSource();
            this.sourceNode.buffer = this.audioBuffer;
            this.sourceNode.connect(this.gainNode);
            this.sourceNode.onended = this.handleEnded;
            
            // Start from paused position
            const offset = this.pauseTime;
            const duration = this.audioBuffer.duration - offset;
            
            this.sourceNode.start(0, offset, duration);
            this.startTime = this.audioContext.currentTime - offset;
            this.isPlaying = true;
            this.isPaused = false;
            
            console.log('Audio resumed from:', offset);
            
        } catch (error) {
            console.error('Failed to resume audio:', error);
            throw new Error(`Audio resume failed: ${error.message}`);
        }
    }
    
    /**
     * Get current playback time in milliseconds
     * @returns {number} Current time in milliseconds
     */
    getCurrentTimeMs() {
        if (!this.isPlaying || !this.audioContext) {
            return this.isPaused ? this.pauseTime * 1000 : 0;
        }
        
        const elapsed = this.audioContext.currentTime - this.startTime;
        return Math.max(0, elapsed * 1000);
    }
    
    /**
     * Get current playback time in seconds
     * @returns {number} Current time in seconds
     */
    getCurrentTimeSeconds() {
        return this.getCurrentTimeMs() / 1000;
    }
    
    /**
     * Get total duration of loaded audio in milliseconds
     * @returns {number} Duration in milliseconds, 0 if no audio loaded
     */
    getDurationMs() {
        return this.audioBuffer ? this.audioBuffer.duration * 1000 : 0;
    }
    
    /**
     * Get total duration of loaded audio in seconds
     * @returns {number} Duration in seconds, 0 if no audio loaded
     */
    getDurationSeconds() {
        return this.audioBuffer ? this.audioBuffer.duration : 0;
    }
    
    /**
     * Set volume (0.0 to 1.0)
     * @param {number} volume - Volume level (0.0 = mute, 1.0 = full volume)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        
        if (this.gainNode) {
            // Use exponential ramp for smooth volume changes
            this.gainNode.gain.setTargetAtTime(
                this.volume,
                this.audioContext.currentTime,
                0.1
            );
        }
    }
    
    /**
     * Get current volume
     * @returns {number} Current volume (0.0 to 1.0)
     */
    getVolume() {
        return this.volume;
    }
    
    /**
     * Check if audio is currently playing
     * @returns {boolean} True if playing
     */
    getIsPlaying() {
        return this.isPlaying;
    }
    
    /**
     * Check if audio is paused
     * @returns {boolean} True if paused
     */
    getIsPaused() {
        return this.isPaused;
    }
    
    /**
     * Check if audio is loaded and ready
     * @returns {boolean} True if audio is loaded
     */
    isReady() {
        return this.audioBuffer !== null;
    }
    
    /**
     * Handle audio playback end
     */
    handleEnded() {
        this.isPlaying = false;
        this.isPaused = false;
        this.startTime = 0;
        this.pauseTime = 0;
        
        if (this.sourceNode) {
            this.sourceNode.disconnect();
            this.sourceNode = null;
        }
        
        console.log('Audio playback ended');
        
        // Call the callback if provided
        if (this.onEndedCallback && typeof this.onEndedCallback === 'function') {
            try {
                this.onEndedCallback();
            } catch (error) {
                console.error('Error in audio ended callback:', error);
            }
        }
    }
    
    /**
     * Get audio context state
     * @returns {string} Audio context state
     */
    getContextState() {
        return this.audioContext ? this.audioContext.state : 'closed';
    }
    
    /**
     * Get audio context sample rate
     * @returns {number} Sample rate in Hz
     */
    getSampleRate() {
        return this.audioContext ? this.audioContext.sampleRate : 0;
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        try {
            // Stop any playing audio
            this.stop();
            
            // Disconnect gain node
            if (this.gainNode) {
                this.gainNode.disconnect();
                this.gainNode = null;
            }
            
            // Close audio context
            if (this.audioContext && this.audioContext.state !== 'closed') {
                this.audioContext.close();
            }
            
            // Clear references
            this.audioContext = null;
            this.audioBuffer = null;
            this.onEndedCallback = null;
            
            console.log('Audio Player cleaned up');
            
        } catch (error) {
            console.error('Error during audio cleanup:', error);
        }
    }
    
    /**
     * Create an audio analyser node for visualization
     * @returns {AnalyserNode} Web Audio API analyser node
     */
    createAnalyser() {
        if (!this.audioContext) {
            throw new Error('Audio context not initialized');
        }
        
        const analyser = this.audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        // Connect to the audio graph
        if (this.gainNode) {
            this.gainNode.connect(analyser);
        }
        
        return analyser;
    }
}
