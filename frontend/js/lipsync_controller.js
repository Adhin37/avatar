/**
 * Lip Sync Controller
 * Synchronizes avatar mouth movements with audio playback based on phoneme timing
 */

export class LipSyncController {
    /**
     * Initialize the Lip Sync Controller
     * @param {AvatarController} avatarController - Avatar controller instance
     * @param {AudioPlayer} audioPlayer - Audio player instance
     */
    constructor(avatarController, audioPlayer) {
        this.avatarController = avatarController;
        this.audioPlayer = audioPlayer;
        
        // Timing data
        this.phonemeTimings = [];
        this.currentTimingIndex = 0;
        this.phonemeMap = {};
        
        // Animation state
        this.isActive = false;
        this.animationId = null;
        this.lastUpdateTime = 0;
        
        // Synchronization settings
        this.syncUpdateInterval = 16; // ~60 FPS (16ms)
        this.lookAheadTime = 50; // Look ahead 50ms for smoother transitions
        this.blendDuration = 100; // Blend between visemes over 100ms
        
        // Current viseme state
        this.currentViseme = 13; // Start with neutral/silence
        this.targetViseme = 13;
        this.visemeTransitionStart = 0;
        this.visemeBlendProgress = 1.0;
        
        // Bind methods
        this.update = this.update.bind(this);
    }
    
    /**
     * Initialize the lip sync controller
     * @param {TTSController} ttsController - TTS controller to get phoneme mapping
     * @returns {Promise<void>}
     */
    async initialize(ttsController) {
        try {
            // Get phoneme to viseme mapping
            if (ttsController) {
                await ttsController.loadPhonemeMap();
                this.phonemeMap = ttsController.getPhonemeMap();
            } else {
                this.phonemeMap = this.getDefaultPhonemeMap();
            }
            
            console.log('Lip Sync Controller initialized with phoneme map:', 
                Object.keys(this.phonemeMap).length, 'phonemes');
            
        } catch (error) {
            console.warn('Failed to load phoneme map, using default:', error);
            this.phonemeMap = this.getDefaultPhonemeMap();
        }
    }
    
    /**
     * Get default phoneme to viseme mapping
     * @returns {Object} Default phoneme mapping
     */
    getDefaultPhonemeMap() {
        return {
            // Vowels - open mouth shapes
            'AH': 0, 'AA': 0, 'AO': 1, 'AW': 1, 'AY': 0,
            'EH': 2, 'ER': 2, 'EY': 2, 'IH': 3, 'IY': 3,
            'OW': 1, 'OY': 1, 'UH': 4, 'UW': 4,
            
            // Consonants - various mouth shapes
            'B': 5, 'P': 5, 'M': 5,  // Bilabial (lips together)
            'F': 6, 'V': 6,          // Labiodental (teeth on lip)
            'TH': 7, 'DH': 7,        // Dental (tongue between teeth)
            'T': 8, 'D': 8, 'N': 8, 'L': 8, 'R': 8,  // Alveolar
            'S': 9, 'Z': 9,          // Sibilants
            'SH': 10, 'ZH': 10, 'CH': 10, 'JH': 10,  // Post-alveolar
            'K': 11, 'G': 11, 'NG': 11,  // Velar
            'HH': 12, 'Y': 12, 'W': 12,  // Glottal/approximants
            'SIL': 13  // Silence/neutral
        };
    }
    
    /**
     * Load phoneme timing data
     * @param {Array} timings - Array of phoneme timing objects
     */
    loadTimings(timings) {
        if (!Array.isArray(timings)) {
            throw new Error('Timings must be an array');
        }
        
        // Process and validate timing data
        this.phonemeTimings = timings.map((timing, index) => {
            const processed = {
                phoneme: timing.phoneme || 'SIL',
                viseme_index: timing.viseme_index !== undefined 
                    ? timing.viseme_index 
                    : this.phonemeMap[timing.phoneme] || 13,
                start_ms: timing.start_ms || 0,
                end_ms: timing.end_ms || 0,
                duration_ms: timing.duration_ms || (timing.end_ms - timing.start_ms),
                index: index
            };
            
            // Validate timing values
            if (processed.end_ms <= processed.start_ms) {
                console.warn(`Invalid timing at index ${index}:`, processed);
                processed.end_ms = processed.start_ms + 50; // Minimum 50ms duration
            }
            
            return processed;
        });
        
        // Sort by start time to ensure correct order
        this.phonemeTimings.sort((a, b) => a.start_ms - b.start_ms);
        
        // Reset state
        this.currentTimingIndex = 0;
        this.currentViseme = 13;
        this.targetViseme = 13;
        
        console.log('Loaded', this.phonemeTimings.length, 'phoneme timings for lip sync');
        
        // Log first few timings for debugging
        if (this.phonemeTimings.length > 0) {
            console.log('First 5 timings:', this.phonemeTimings.slice(0, 5));
        }
    }
    
    /**
     * Start the lip sync animation
     */
    start() {
        if (this.isActive) {
            console.warn('Lip sync already active');
            return;
        }
        
        if (!this.phonemeTimings || this.phonemeTimings.length === 0) {
            console.warn('No phoneme timings loaded');
            return;
        }
        
        if (!this.audioPlayer || !this.avatarController) {
            throw new Error('Avatar controller and audio player required');
        }
        
        this.isActive = true;
        this.lastUpdateTime = performance.now();
        this.currentTimingIndex = 0;
        this.currentViseme = 13; // Start with neutral
        this.targetViseme = 13;
        
        console.log('Lip sync started');
        this.scheduleUpdate();
    }
    
    /**
     * Stop the lip sync animation
     */
    stop() {
        if (!this.isActive) {
            return;
        }
        
        this.isActive = false;
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        // Reset to neutral viseme
        this.resetToNeutral();
        
        console.log('Lip sync stopped');
    }
    
    /**
     * Schedule the next update frame
     */
    scheduleUpdate() {
        if (!this.isActive) {
            return;
        }
        
        this.animationId = requestAnimationFrame(this.update);
    }
    
    /**
     * Update lip sync animation
     */
    update() {
        if (!this.isActive) {
            return;
        }
        
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastUpdateTime;
        
        // Throttle updates to target framerate
        if (deltaTime >= this.syncUpdateInterval) {
            this.updateLipSync();
            this.lastUpdateTime = currentTime;
        }
        
        // Schedule next frame
        this.scheduleUpdate();
    }
    
    /**
     * Update lip sync based on current audio time
     */
    updateLipSync() {
        try {
            // Get current audio playback time
            const audioTimeMs = this.audioPlayer.getCurrentTimeMs();
            
            // Find current and upcoming phonemes
            const currentTiming = this.findCurrentTiming(audioTimeMs);
            const nextTiming = this.findNextTiming(audioTimeMs);
            
            // Update viseme based on current timing
            this.updateViseme(currentTiming, nextTiming, audioTimeMs);
            
        } catch (error) {
            console.error('Error updating lip sync:', error);
        }
    }
    
    /**
     * Find the phoneme timing that should be active at the given time
     * @param {number} timeMs - Current time in milliseconds
     * @returns {Object|null} Current timing object or null
     */
    findCurrentTiming(timeMs) {
        for (let i = this.currentTimingIndex; i < this.phonemeTimings.length; i++) {
            const timing = this.phonemeTimings[i];
            
            if (timeMs >= timing.start_ms && timeMs < timing.end_ms) {
                this.currentTimingIndex = i;
                return timing;
            }
            
            // If we've passed this timing, move to the next one
            if (timeMs >= timing.end_ms) {
                this.currentTimingIndex = i + 1;
            }
        }
        
        // Check previous timings in case we missed one
        for (let i = Math.max(0, this.currentTimingIndex - 5); i < this.currentTimingIndex; i++) {
            const timing = this.phonemeTimings[i];
            if (timeMs >= timing.start_ms && timeMs < timing.end_ms) {
                this.currentTimingIndex = i;
                return timing;
            }
        }
        
        return null;
    }
    
    /**
     * Find the next phoneme timing after the given time
     * @param {number} timeMs - Current time in milliseconds
     * @returns {Object|null} Next timing object or null
     */
    findNextTiming(timeMs) {
        const lookAheadMs = timeMs + this.lookAheadTime;
        
        for (let i = this.currentTimingIndex; i < this.phonemeTimings.length; i++) {
            const timing = this.phonemeTimings[i];
            
            if (timing.start_ms > timeMs && timing.start_ms <= lookAheadMs) {
                return timing;
            }
        }
        
        return null;
    }
    
    /**
     * Update the current viseme based on timing information
     * @param {Object|null} currentTiming - Current phoneme timing
     * @param {Object|null} nextTiming - Next phoneme timing
     * @param {number} audioTimeMs - Current audio time
     */
    updateViseme(currentTiming, nextTiming, audioTimeMs) {
        let targetVisemeIndex = 13; // Default to neutral
        
        if (currentTiming) {
            targetVisemeIndex = currentTiming.viseme_index;
        } else if (nextTiming && (nextTiming.start_ms - audioTimeMs) <= this.lookAheadTime) {
            // Pre-shape for upcoming phoneme
            targetVisemeIndex = nextTiming.viseme_index;
        }
        
        // Check if we need to transition to a new viseme
        if (this.targetViseme !== targetVisemeIndex) {
            this.startVisemeTransition(targetVisemeIndex);
        }
        
        // Update blend progress
        this.updateVisemeBlend(audioTimeMs);
        
        // Apply to avatar
        this.applyVisemeToAvatar();
    }
    
    /**
     * Start a transition to a new viseme
     * @param {number} newVisemeIndex - Target viseme index
     */
    startVisemeTransition(newVisemeIndex) {
        this.currentViseme = this.targetViseme;
        this.targetViseme = newVisemeIndex;
        this.visemeTransitionStart = performance.now();
        this.visemeBlendProgress = 0.0;
        
        // console.log(`Transitioning from viseme ${this.currentViseme} to ${this.targetViseme}`);
    }
    
    /**
     * Update viseme blend progress
     * @param {number} audioTimeMs - Current audio time
     */
    updateVisemeBlend(audioTimeMs) {
        if (this.currentViseme === this.targetViseme) {
            this.visemeBlendProgress = 1.0;
            return;
        }
        
        const elapsedMs = performance.now() - this.visemeTransitionStart;
        this.visemeBlendProgress = Math.min(1.0, elapsedMs / this.blendDuration);
        
        // Use easing for smoother transitions
        this.visemeBlendProgress = this.easeInOutCubic(this.visemeBlendProgress);
    }
    
    /**
     * Apply current viseme state to the avatar
     */
    applyVisemeToAvatar() {
        if (!this.avatarController) {
            return;
        }
        
        // Reset all viseme weights
        for (let i = 0; i < 14; i++) {
            this.avatarController.setViseme(i, 0.0);
        }
        
        // Apply current viseme blend
        if (this.visemeBlendProgress >= 1.0) {
            // Fully transitioned to target viseme
            this.avatarController.setViseme(this.targetViseme, 1.0);
        } else {
            // Blend between current and target visemes
            const currentWeight = 1.0 - this.visemeBlendProgress;
            const targetWeight = this.visemeBlendProgress;
            
            if (currentWeight > 0) {
                this.avatarController.setViseme(this.currentViseme, currentWeight);
            }
            if (targetWeight > 0) {
                this.avatarController.setViseme(this.targetViseme, targetWeight);
            }
        }
    }
    
    /**
     * Reset avatar to neutral position
     */
    resetToNeutral() {
        if (!this.avatarController) {
            return;
        }
        
        // Clear all viseme weights
        for (let i = 0; i < 14; i++) {
            this.avatarController.setViseme(i, 0.0);
        }
        
        // Set neutral viseme
        this.avatarController.setViseme(13, 1.0);
        
        this.currentViseme = 13;
        this.targetViseme = 13;
    }
    
    /**
     * Cubic easing function for smooth transitions
     * @param {number} t - Progress value (0-1)
     * @returns {number} Eased value (0-1)
     */
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    /**
     * Get current lip sync status
     * @returns {Object} Status information
     */
    getStatus() {
        return {
            isActive: this.isActive,
            currentViseme: this.currentViseme,
            targetViseme: this.targetViseme,
            blendProgress: this.visemeBlendProgress,
            currentTimingIndex: this.currentTimingIndex,
            totalTimings: this.phonemeTimings.length,
            audioTime: this.audioPlayer ? this.audioPlayer.getCurrentTimeMs() : 0
        };
    }
    
    /**
     * Debug function to log current timing information
     */
    logCurrentTiming() {
        const audioTimeMs = this.audioPlayer ? this.audioPlayer.getCurrentTimeMs() : 0;
        const currentTiming = this.findCurrentTiming(audioTimeMs);
        const nextTiming = this.findNextTiming(audioTimeMs);
        
        console.log('Lip Sync Debug:', {
            audioTime: audioTimeMs,
            currentTiming: currentTiming,
            nextTiming: nextTiming,
            currentViseme: this.currentViseme,
            targetViseme: this.targetViseme,
            blendProgress: this.visemeBlendProgress
        });
    }
    
    /**
     * Set lip sync parameters
     * @param {Object} params - Parameters to update
     */
    setParameters(params) {
        if (params.lookAheadTime !== undefined) {
            this.lookAheadTime = Math.max(0, params.lookAheadTime);
        }
        
        if (params.blendDuration !== undefined) {
            this.blendDuration = Math.max(10, params.blendDuration);
        }
        
        if (params.syncUpdateInterval !== undefined) {
            this.syncUpdateInterval = Math.max(8, params.syncUpdateInterval);
        }
        
        console.log('Lip sync parameters updated:', {
            lookAheadTime: this.lookAheadTime,
            blendDuration: this.blendDuration,
            syncUpdateInterval: this.syncUpdateInterval
        });
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        this.stop();
        this.phonemeTimings = [];
        this.currentTimingIndex = 0;
        this.avatarController = null;
        this.audioPlayer = null;
        
        console.log('Lip Sync Controller cleaned up');
    }
}
