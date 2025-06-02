/**
 * Audio Player
 * Handles audio decoding, playback, and timing queries using Web Audio API
 */

export class AudioPlayer {
    constructor() {
        this.audioContext = null;
        this.audioBuffer = null;
        this.sourceNode = null;
        this.gainNode = null;
        
        this.isPlaying = false;
        this.isPaused = false;
        this.startTime = 0;
        this.pauseTime = 0;
        this.volume = 0.8;
        
        this.onEndedCallback = null;
        
        this.handleEnded = this.handleEnded.bind(this);
    }
    
    async initialize() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            this.gainNode = this.audioContext.createGain();
            this.gainNode.connect(this.audioContext.destination);
            this.gainNode.gain.value = this.volume;
            
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            console.log('Audio Player initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize Audio Player:', error);
            throw new Error(`Audio initialization failed: ${error.message}`);
        }
    }
    
    async loadBase64Audio(base64Data) {
        if (!this.audioContext) {
            throw new Error('Audio context not initialized');
        }
        
        if (!base64Data || typeof base64Data !== 'string') {
            throw new Error('Invalid base64 audio data');
        }
        
        try {
            const binaryString = atob(base64Data);
            const arrayBuffer = new ArrayBuffer(binaryString.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < binaryString.length; i++) {
                uint8Array[i] = binaryString.charCodeAt(i);
            }
            
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
    
    async play(onEndedCallback = null) {
        if (!this.audioBuffer) {
            throw new Error('No audio loaded');
        }
        
        if (this.isPlaying) {
            console.warn('Audio is already playing');
            return;
        }
        
        try {
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            this.sourceNode = this.audioContext.createBufferSource();
            this.sourceNode.buffer = this.audioBuffer;
            this.sourceNode.connect(this.gainNode);
            
            this.onEndedCallback = onEndedCallback;
            this.sourceNode.onended = this.handleEnded;
            
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
    
    pause() {
        if (!this.isPlaying || this.isPaused) {
            return;
        }
        
        this.pauseTime = this.getCurrentTimeMs() / 1000;
        this.stop();
        this.isPaused = true;
        
        console.log('Audio paused at:', this.pauseTime);
    }
    
    async resume() {
        if (!this.isPaused || !this.audioBuffer) {
            return;
        }
        
        try {
            this.sourceNode = this.audioContext.createBufferSource();
            this.sourceNode.buffer = this.audioBuffer;
            this.sourceNode.connect(this.gainNode);
            this.sourceNode.onended = this.handleEnded;
            
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
    
    getCurrentTimeMs() {
        if (!this.isPlaying || !this.audioContext) {
            return this.isPaused ? this.pauseTime * 1000 : 0;
        }
        
        const elapsed = this.audioContext.currentTime - this.startTime;
        return Math.max(0, elapsed * 1000);
    }
    
    getCurrentTimeSeconds() {
        return this.getCurrentTimeMs() / 1000;
    }
    
    getDurationMs() {
        return this.audioBuffer ? this.audioBuffer.duration * 1000 : 0;
    }
    
    getDurationSeconds() {
        return this.audioBuffer ? this.audioBuffer.duration : 0;
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        
        if (this.gainNode) {
            this.gainNode.gain.setTargetAtTime(
                this.volume,
                this.audioContext.currentTime,
                0.1
            );
        }
    }
    
    getVolume() {
        return this.volume;
    }
    
    getIsPlaying() {
        return this.isPlaying;
    }
    
    getIsPaused() {
        return this.isPaused;
    }
    
    isReady() {
        return this.audioBuffer !== null;
    }
    
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
        
        if (this.onEndedCallback && typeof this.onEndedCallback === 'function') {
            try {
                this.onEndedCallback();
            } catch (error) {
                console.error('Error in audio ended callback:', error);
            }
        }
    }
    
    getContextState() {
        return this.audioContext ? this.audioContext.state : 'closed';
    }
    
    getSampleRate() {
        return this.audioContext ? this.audioContext.sampleRate : 0;
    }
    
    cleanup() {
        try {
            this.stop();
            
            if (this.gainNode) {
                this.gainNode.disconnect();
                this.gainNode = null;
            }
            
            if (this.audioContext && this.audioContext.state !== 'closed') {
                this.audioContext.close();
            }
            
            this.audioContext = null;
            this.audioBuffer = null;
            this.onEndedCallback = null;
            
            console.log('Audio Player cleaned up');
            
        } catch (error) {
            console.error('Error during audio cleanup:', error);
        }
    }
    
    createAnalyser() {
        if (!this.audioContext) {
            throw new Error('Audio context not initialized');
        }
        
        const analyser = this.audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        if (this.gainNode) {
            this.gainNode.connect(analyser);
        }
        
        return analyser;
    }
    
    applyAudioEffects(effects = {}) {
        if (!this.audioContext || !this.sourceNode) {
            console.warn('Cannot apply effects: audio context or source not available');
            return;
        }
        
        try {
            if (effects.reverb) {
                const convolver = this.audioContext.createConvolver();
                // Create impulse response for reverb
                const impulseLength = this.audioContext.sampleRate * 2;
                const impulse = this.audioContext.createBuffer(2, impulseLength, this.audioContext.sampleRate);
                
                for (let channel = 0; channel < 2; channel++) {
                    const channelData = impulse.getChannelData(channel);
                    for (let i = 0; i < impulseLength; i++) {
                        channelData[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / impulseLength, 2);
                    }
                }
                
                convolver.buffer = impulse;
                this.sourceNode.connect(convolver);
                convolver.connect(this.gainNode);
            }
            
            if (effects.lowpass) {
                const filter = this.audioContext.createBiquadFilter();
                filter.type = 'lowpass';
                filter.frequency.value = effects.lowpass.frequency || 1000;
                filter.Q.value = effects.lowpass.Q || 1;
                
                this.sourceNode.connect(filter);
                filter.connect(this.gainNode);
            }
            
            if (effects.highpass) {
                const filter = this.audioContext.createBiquadFilter();
                filter.type = 'highpass';
                filter.frequency.value = effects.highpass.frequency || 200;
                filter.Q.value = effects.highpass.Q || 1;
                
                this.sourceNode.connect(filter);
                filter.connect(this.gainNode);
            }
            
            if (effects.distortion) {
                const waveshaper = this.audioContext.createWaveShaper();
                const amount = effects.distortion.amount || 50;
                const samples = 44100;
                const curve = new Float32Array(samples);
                const deg = Math.PI / 180;
                
                for (let i = 0; i < samples; i++) {
                    const x = (i * 2) / samples - 1;
                    curve[i] = ((3 + amount) * x * 20 * deg) / (Math.PI + amount * Math.abs(x));
                }
                
                waveshaper.curve = curve;
                waveshaper.oversample = '4x';
                
                this.sourceNode.connect(waveshaper);
                waveshaper.connect(this.gainNode);
            }
            
            console.log('Audio effects applied:', Object.keys(effects));
            
        } catch (error) {
            console.error('Failed to apply audio effects:', error);
        }
    }
    
    getAudioData() {
        if (!this.audioBuffer) {
            return null;
        }
        
        const channelData = [];
        for (let channel = 0; channel < this.audioBuffer.numberOfChannels; channel++) {
            channelData.push(this.audioBuffer.getChannelData(channel));
        }
        
        return {
            duration: this.audioBuffer.duration,
            sampleRate: this.audioBuffer.sampleRate,
            numberOfChannels: this.audioBuffer.numberOfChannels,
            length: this.audioBuffer.length,
            channelData: channelData
        };
    }
    
    getPlaybackInfo() {
        return {
            isPlaying: this.isPlaying,
            isPaused: this.isPaused,
            currentTime: this.getCurrentTimeSeconds(),
            duration: this.getDurationSeconds(),
            volume: this.volume,
            sampleRate: this.getSampleRate(),
            contextState: this.getContextState()
        };
    }
}