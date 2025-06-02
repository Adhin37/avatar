/**
 * Lip Sync Controller
 * Synchronizes avatar mouth movements with audio playback based on phoneme timing
 * Integrates with advanced facial expression system
 */

export class LipSyncController {
    constructor(avatarController, audioPlayer) {
        this.avatarController = avatarController;
        this.audioPlayer = audioPlayer;
        
        this.phonemeTimings = [];
        this.currentTimingIndex = 0;
        this.phonemeMap = {};
        
        this.isActive = false;
        this.animationId = null;
        this.lastUpdateTime = 0;
        
        this.syncUpdateInterval = 16;
        this.lookAheadTime = 50;
        this.blendDuration = 100;
        this.expressionInfluence = 0.3;
        
        this.currentViseme = 13;
        this.targetViseme = 13;
        this.visemeTransitionStart = 0;
        this.visemeBlendProgress = 1.0;
        
        this.emotionalModulation = {
            enabled: true,
            intensity: 0.2,
            currentEmotion: 'neutral'
        };
        
        this.adaptiveSync = {
            enabled: true,
            confidenceThreshold: 0.7,
            adaptiveBlending: true,
            performanceMode: 'balanced'
        };
        
        this.update = this.update.bind(this);
    }
    
    async initialize(ttsController) {
        try {
            if (ttsController) {
                await ttsController.loadPhonemeMap();
                this.phonemeMap = ttsController.getPhonemeMap();
            } else {
                this.phonemeMap = this.getDefaultPhonemeMap();
            }
            
            this.setupVisemeBlending();
            this.initializeAdaptiveFeatures();
            
            console.log('Lip Sync Controller initialized with phoneme map:', 
                Object.keys(this.phonemeMap).length, 'phonemes');
            
        } catch (error) {
            console.warn('Failed to load phoneme map, using default:', error);
            this.phonemeMap = this.getDefaultPhonemeMap();
        }
    }
    
    setupVisemeBlending() {
        this.visemeBlendWeights = new Array(14).fill(0);
        this.targetVisemeWeights = new Array(14).fill(0);
        this.visemeCoarticulation = {
            enabled: true,
            strength: 0.3,
            windowSize: 3
        };
    }
    
    initializeAdaptiveFeatures() {
        this.adaptiveSync.performanceMetrics = {
            frameRate: 60,
            processingTime: 0,
            syncAccuracy: 1.0
        };
        
        this.emotionalInfluenceMap = {
            happy: { intensity: 1.2, openness: 1.1, roundness: 0.9 },
            sad: { intensity: 0.8, openness: 0.9, roundness: 1.1 },
            angry: { intensity: 1.3, openness: 0.8, roundness: 0.8 },
            surprised: { intensity: 1.4, openness: 1.3, roundness: 1.2 },
            fearful: { intensity: 0.9, openness: 1.1, roundness: 1.0 },
            disgusted: { intensity: 0.7, openness: 0.7, roundness: 0.8 },
            neutral: { intensity: 1.0, openness: 1.0, roundness: 1.0 }
        };
    }
    
    getDefaultPhonemeMap() {
        return {
            'AH': 0, 'AA': 0, 'AO': 1, 'AW': 1, 'AY': 0,
            'EH': 2, 'ER': 2, 'EY': 2, 'IH': 3, 'IY': 3,
            'OW': 1, 'OY': 1, 'UH': 4, 'UW': 4,
            
            'B': 5, 'P': 5, 'M': 5,
            'F': 6, 'V': 6,
            'TH': 7, 'DH': 7,
            'T': 8, 'D': 8, 'N': 8, 'L': 8, 'R': 8,
            'S': 9, 'Z': 9,
            'SH': 10, 'ZH': 10, 'CH': 10, 'JH': 10,
            'K': 11, 'G': 11, 'NG': 11,
            'HH': 12, 'Y': 12, 'W': 12,
            'SIL': 13
        };
    }
    
    loadTimings(timings) {
        if (!Array.isArray(timings)) {
            throw new Error('Timings must be an array');
        }
        
        this.phonemeTimings = timings.map((timing, index) => {
            const processed = {
                phoneme: timing.phoneme || 'SIL',
                viseme_index: timing.viseme_index !== undefined 
                    ? timing.viseme_index 
                    : this.phonemeMap[timing.phoneme] || 13,
                start_ms: timing.start_ms || 0,
                end_ms: timing.end_ms || 0,
                duration_ms: timing.duration_ms || (timing.end_ms - timing.start_ms),
                confidence: timing.confidence || 1.0,
                index: index
            };
            
            if (processed.end_ms <= processed.start_ms) {
                console.warn(`Invalid timing at index ${index}:`, processed);
                processed.end_ms = processed.start_ms + 50;
            }
            
            return processed;
        });
        
        this.phonemeTimings.sort((a, b) => a.start_ms - b.start_ms);
        
        if (this.visemeCoarticulation.enabled) {
            this.applyCoarticulation();
        }
        
        this.currentTimingIndex = 0;
        this.currentViseme = 13;
        this.targetViseme = 13;
        
        console.log('Loaded', this.phonemeTimings.length, 'phoneme timings for lip sync');
        
        if (this.phonemeTimings.length > 0) {
            console.log('First 5 timings:', this.phonemeTimings.slice(0, 5));
        }
    }
    
    applyCoarticulation() {
        const windowSize = this.visemeCoarticulation.windowSize;
        const strength = this.visemeCoarticulation.strength;
        
        for (let i = 0; i < this.phonemeTimings.length; i++) {
            const current = this.phonemeTimings[i];
            const neighbors = [];
            
            for (let j = Math.max(0, i - windowSize); j <= Math.min(this.phonemeTimings.length - 1, i + windowSize); j++) {
                if (j !== i) {
                    neighbors.push(this.phonemeTimings[j]);
                }
            }
            
            current.coarticulation = neighbors.map(neighbor => ({
                viseme_index: neighbor.viseme_index,
                influence: strength * Math.exp(-Math.abs(neighbor.start_ms - current.start_ms) / 100)
            }));
        }
    }
    
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
        this.currentViseme = 13;
        this.targetViseme = 13;
        
        this.resetVisemeWeights();
        
        if (this.avatarController.getExpressionStates) {
            const expressions = this.avatarController.getExpressionStates();
            this.updateEmotionalContext(expressions);
        }
        
        console.log('Lip sync started with advanced features');
        this.scheduleUpdate();
    }
    
    updateEmotionalContext(expressions) {
        let dominantEmotion = 'neutral';
        let maxIntensity = 0;
        
        const emotions = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted'];
        emotions.forEach(emotion => {
            if (expressions[emotion] && expressions[emotion] > maxIntensity) {
                maxIntensity = expressions[emotion];
                dominantEmotion = emotion;
            }
        });
        
        this.emotionalModulation.currentEmotion = dominantEmotion;
        this.emotionalModulation.intensity = maxIntensity;
    }
    
    stop() {
        if (!this.isActive) {
            return;
        }
        
        this.isActive = false;
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        this.resetToNeutral();
        
        console.log('Lip sync stopped');
    }
    
    scheduleUpdate() {
        if (!this.isActive) {
            return;
        }
        
        this.animationId = requestAnimationFrame(this.update);
    }
    
    update() {
        if (!this.isActive) {
            return;
        }
        
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastUpdateTime;
        
        if (deltaTime >= this.syncUpdateInterval) {
            const processingStart = performance.now();
            
            this.updateLipSync();
            
            const processingTime = performance.now() - processingStart;
            this.updatePerformanceMetrics(processingTime, deltaTime);
            
            this.lastUpdateTime = currentTime;
        }
        
        this.scheduleUpdate();
    }
    
    updateLipSync() {
        try {
            const audioTimeMs = this.audioPlayer.getCurrentTimeMs();
            
            const currentTiming = this.findCurrentTiming(audioTimeMs);
            const nextTiming = this.findNextTiming(audioTimeMs);
            
            this.updateViseme(currentTiming, nextTiming, audioTimeMs);
            this.updateVisemeBlending();
            this.applyEmotionalModulation();
            this.applyToAvatar();
            
        } catch (error) {
            console.error('Error updating lip sync:', error);
        }
    }
    
    findCurrentTiming(timeMs) {
        for (let i = this.currentTimingIndex; i < this.phonemeTimings.length; i++) {
            const timing = this.phonemeTimings[i];
            
            if (timeMs >= timing.start_ms && timeMs < timing.end_ms) {
                this.currentTimingIndex = i;
                return timing;
            }
            
            if (timeMs >= timing.end_ms) {
                this.currentTimingIndex = i + 1;
            }
        }
        
        for (let i = Math.max(0, this.currentTimingIndex - 5); i < this.currentTimingIndex; i++) {
            const timing = this.phonemeTimings[i];
            if (timeMs >= timing.start_ms && timeMs < timing.end_ms) {
                this.currentTimingIndex = i;
                return timing;
            }
        }
        
        return null;
    }
    
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
    
    updateViseme(currentTiming, nextTiming, audioTimeMs) {
        let targetVisemeIndex = 13;
        let confidence = 1.0;
        
        if (currentTiming) {
            targetVisemeIndex = currentTiming.viseme_index;
            confidence = currentTiming.confidence || 1.0;
        } else if (nextTiming && (nextTiming.start_ms - audioTimeMs) <= this.lookAheadTime) {
            targetVisemeIndex = nextTiming.viseme_index;
            confidence = nextTiming.confidence || 1.0;
        }
        
        if (this.targetViseme !== targetVisemeIndex) {
            this.startVisemeTransition(targetVisemeIndex, confidence);
        }
        
        this.updateVisemeBlendProgress(audioTimeMs);
        
        if (this.visemeCoarticulation.enabled && currentTiming && currentTiming.coarticulation) {
            this.applyCoarticulationEffects(currentTiming.coarticulation);
        }
    }
    
    startVisemeTransition(newVisemeIndex, confidence = 1.0) {
        this.currentViseme = this.targetViseme;
        this.targetViseme = newVisemeIndex;
        this.visemeTransitionStart = performance.now();
        this.visemeBlendProgress = 0.0;
        
        if (this.adaptiveSync.enabled && confidence < this.adaptiveSync.confidenceThreshold) {
            this.blendDuration *= 1.5;
        }
    }
    
    updateVisemeBlendProgress(audioTimeMs) {
        if (this.currentViseme === this.targetViseme) {
            this.visemeBlendProgress = 1.0;
            return;
        }
        
        const elapsedMs = performance.now() - this.visemeTransitionStart;
        this.visemeBlendProgress = Math.min(1.0, elapsedMs / this.blendDuration);
        
        this.visemeBlendProgress = this.easeInOutCubic(this.visemeBlendProgress);
    }
    
    updateVisemeBlending() {
        this.targetVisemeWeights.fill(0);
        
        if (this.visemeBlendProgress >= 1.0) {
            this.targetVisemeWeights[this.targetViseme] = 1.0;
        } else {
            const currentWeight = 1.0 - this.visemeBlendProgress;
            const targetWeight = this.visemeBlendProgress;
            
            if (currentWeight > 0) {
                this.targetVisemeWeights[this.currentViseme] = currentWeight;
            }
            if (targetWeight > 0) {
                this.targetVisemeWeights[this.targetViseme] = targetWeight;
            }
        }
        
        for (let i = 0; i < this.visemeBlendWeights.length; i++) {
            const target = this.targetVisemeWeights[i];
            const current = this.visemeBlendWeights[i];
            const diff = target - current;
            
            this.visemeBlendWeights[i] += diff * 0.15;
            
            if (Math.abs(diff) < 0.001) {
                this.visemeBlendWeights[i] = target;
            }
        }
    }
    
    applyCoarticulationEffects(coarticulation) {
        coarticulation.forEach(effect => {
            const visemeIndex = effect.viseme_index;
            const influence = effect.influence;
            
            if (visemeIndex >= 0 && visemeIndex < this.targetVisemeWeights.length) {
                this.targetVisemeWeights[visemeIndex] += influence;
                this.targetVisemeWeights[visemeIndex] = Math.min(1.0, this.targetVisemeWeights[visemeIndex]);
            }
        });
    }
    
    applyEmotionalModulation() {
        if (!this.emotionalModulation.enabled) {
            return;
        }
        
        const emotion = this.emotionalModulation.currentEmotion;
        const intensity = this.emotionalModulation.intensity;
        const influence = this.emotionalInfluenceMap[emotion] || this.emotionalInfluenceMap.neutral;
        
        for (let i = 0; i < this.visemeBlendWeights.length; i++) {
            if (this.visemeBlendWeights[i] > 0) {
                let modulation = 1.0;
                
                if ([0, 1, 2, 3, 4].includes(i)) {
                    modulation *= influence.openness;
                }
                if ([1, 4].includes(i)) {
                    modulation *= influence.roundness;
                }
                
                modulation *= influence.intensity;
                
                const emotionalInfluence = this.expressionInfluence * intensity;
                this.visemeBlendWeights[i] = this.visemeBlendWeights[i] * (1 - emotionalInfluence) + 
                                           (this.visemeBlendWeights[i] * modulation) * emotionalInfluence;
            }
        }
    }
    
    applyToAvatar() {
        if (!this.avatarController) {
            return;
        }
        
        for (let i = 0; i < this.visemeBlendWeights.length; i++) {
            this.avatarController.setViseme(i, this.visemeBlendWeights[i]);
        }
    }
    
    resetVisemeWeights() {
        this.visemeBlendWeights.fill(0);
        this.targetVisemeWeights.fill(0);
        this.visemeBlendWeights[13] = 1.0;
        this.targetVisemeWeights[13] = 1.0;
    }
    
    resetToNeutral() {
        if (!this.avatarController) {
            return;
        }
        
        for (let i = 0; i < 14; i++) {
            this.avatarController.setViseme(i, 0.0);
        }
        
        this.avatarController.setViseme(13, 1.0);
        
        this.currentViseme = 13;
        this.targetViseme = 13;
        this.resetVisemeWeights();
    }
    
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    updatePerformanceMetrics(processingTime, deltaTime) {
        this.adaptiveSync.performanceMetrics.processingTime = processingTime;
        this.adaptiveSync.performanceMetrics.frameRate = 1000 / deltaTime;
        
        if (this.adaptiveSync.performanceMetrics.frameRate < 30) {
            this.adaptiveSync.performanceMode = 'performance';
            this.syncUpdateInterval = 20;
        } else if (this.adaptiveSync.performanceMetrics.frameRate > 55) {
            this.adaptiveSync.performanceMode = 'quality';
            this.syncUpdateInterval = 16;
        }
    }
    
    getStatus() {
        return {
            isActive: this.isActive,
            currentViseme: this.currentViseme,
            targetViseme: this.targetViseme,
            blendProgress: this.visemeBlendProgress,
            currentTimingIndex: this.currentTimingIndex,
            totalTimings: this.phonemeTimings.length,
            audioTime: this.audioPlayer ? this.audioPlayer.getCurrentTimeMs() : 0,
            emotionalModulation: this.emotionalModulation,
            performanceMetrics: this.adaptiveSync.performanceMetrics,
            visemeWeights: [...this.visemeBlendWeights]
        };
    }
    
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
            blendProgress: this.visemeBlendProgress,
            emotionalContext: this.emotionalModulation.currentEmotion,
            performanceMode: this.adaptiveSync.performanceMode
        });
    }
    
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
        
        if (params.expressionInfluence !== undefined) {
            this.expressionInfluence = Math.max(0, Math.min(1, params.expressionInfluence));
        }
        
        if (params.emotionalModulation !== undefined) {
            this.emotionalModulation.enabled = params.emotionalModulation;
        }
        
        if (params.coarticulation !== undefined) {
            this.visemeCoarticulation.enabled = params.coarticulation;
        }
        
        if (params.adaptiveSync !== undefined) {
            this.adaptiveSync.enabled = params.adaptiveSync;
        }
        
        console.log('Lip sync parameters updated:', {
            lookAheadTime: this.lookAheadTime,
            blendDuration: this.blendDuration,
            syncUpdateInterval: this.syncUpdateInterval,
            expressionInfluence: this.expressionInfluence,
            emotionalModulation: this.emotionalModulation.enabled,
            coarticulation: this.visemeCoarticulation.enabled,
            adaptiveSync: this.adaptiveSync.enabled
        });
    }
    
    getAdvancedMetrics() {
        return {
            syncAccuracy: this.calculateSyncAccuracy(),
            emotionalInfluence: this.expressionInfluence,
            coarticulationStrength: this.visemeCoarticulation.strength,
            adaptiveFeatures: this.adaptiveSync,
            visemeDistribution: this.getVisemeDistribution(),
            performanceProfile: this.getPerformanceProfile()
        };
    }
    
    calculateSyncAccuracy() {
        if (!this.phonemeTimings.length || !this.audioPlayer) {
            return 1.0;
        }
        
        const audioTime = this.audioPlayer.getCurrentTimeMs();
        const timing = this.findCurrentTiming(audioTime);
        
        if (!timing) {
            return 1.0;
        }
        
        const timingCenter = (timing.start_ms + timing.end_ms) / 2;
        const offset = Math.abs(audioTime - timingCenter);
        const maxOffset = (timing.end_ms - timing.start_ms) / 2;
        
        return Math.max(0, 1 - (offset / maxOffset));
    }
    
    getVisemeDistribution() {
        const distribution = new Array(14).fill(0);
        let total = 0;
        
        this.phonemeTimings.forEach(timing => {
            if (timing.viseme_index >= 0 && timing.viseme_index < 14) {
                distribution[timing.viseme_index] += timing.duration_ms;
                total += timing.duration_ms;
            }
        });
        
        return distribution.map(count => total > 0 ? count / total : 0);
    }
    
    getPerformanceProfile() {
        return {
            averageFrameRate: this.adaptiveSync.performanceMetrics.frameRate,
            averageProcessingTime: this.adaptiveSync.performanceMetrics.processingTime,
            currentMode: this.adaptiveSync.performanceMode,
            adaptationsApplied: this.adaptiveSync.enabled ? 'enabled' : 'disabled'
        };
    }
    
    cleanup() {
        this.stop();
        this.phonemeTimings = [];
        this.currentTimingIndex = 0;
        this.avatarController = null;
        this.audioPlayer = null;
        
        console.log('Lip Sync Controller cleaned up');
    }
}