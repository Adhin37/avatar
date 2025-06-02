/**
 * TTS Controller
 * Handles communication with the local TTS server for speech synthesis
 */

export class TTSController {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.phonemeMap = null;
        this.isAvailable = false;
        
        this.healthTimeout = 5000;
        this.synthesisTimeout = 30000;
    }
    
    async checkHealth() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.healthTimeout);
            
            const response = await fetch(`${this.serverUrl}/health`, {
                method: 'GET',
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
            }
            
            const healthData = await response.json();
            this.isAvailable = healthData.status === 'healthy' && healthData.tts_ready;
            
            if (!this.isAvailable) {
                throw new Error('TTS server not ready');
            }
            
            return true;
            
        } catch (error) {
            this.isAvailable = false;
            
            if (error.name === 'AbortError') {
                throw new Error('TTS server connection timeout');
            } else if (error.code === 'ECONNREFUSED' || error.message.includes('fetch')) {
                throw new Error('TTS server not running. Please start the Python server.');
            } else {
                throw new Error(`TTS server health check failed: ${error.message}`);
            }
        }
    }
    
    async loadPhonemeMap() {
        try {
            const response = await fetch(`${this.serverUrl}/phoneme-map`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to load phoneme map: ${response.status}`);
            }
            
            this.phonemeMap = await response.json();
            return this.phonemeMap;
            
        } catch (error) {
            console.warn('Failed to load phoneme map from server, using default:', error);
            
            this.phonemeMap = this.getDefaultPhonemeMap();
            return this.phonemeMap;
        }
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
    
    async synthesize(text, speed = 1.0) {
        if (!this.isAvailable) {
            throw new Error('TTS server not available');
        }
        
        if (!text || typeof text !== 'string') {
            throw new Error('Invalid text input');
        }
        
        if (text.length > 1000) {
            throw new Error('Text too long (maximum 1000 characters)');
        }
        
        if (speed < 0.1 || speed > 5.0) {
            throw new Error('Speed must be between 0.1 and 5.0');
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.synthesisTimeout);
            
            const requestBody = {
                text: text.trim(),
                speed: speed
            };
            
            console.log('Sending TTS request:', requestBody);
            
            const response = await fetch(`${this.serverUrl}/synthesize`, {
                method: 'POST',
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Synthesis failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (!result.audio_data || !result.phoneme_timings) {
                throw new Error('Invalid response format from TTS server');
            }
            
            const processedTimings = this.processPhonemeTimings(result.phoneme_timings);
            
            console.log('TTS synthesis successful:', {
                duration: result.duration,
                timings: processedTimings.length,
                sampleRate: result.sample_rate
            });
            
            return {
                audio_data: result.audio_data,
                phoneme_timings: processedTimings,
                duration: result.duration,
                sample_rate: result.sample_rate
            };
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('TTS synthesis timeout');
            } else {
                throw new Error(`TTS synthesis failed: ${error.message}`);
            }
        }
    }
    
    processPhonemeTimings(timings) {
        if (!this.phonemeMap) {
            console.warn('No phoneme map available, using default');
            this.phonemeMap = this.getDefaultPhonemeMap();
        }
        
        return timings.map(timing => {
            const phoneme = timing.phoneme.toUpperCase();
            const visemeIndex = this.phonemeMap[phoneme] !== undefined 
                ? this.phonemeMap[phoneme] 
                : this.phonemeMap['SIL'];
            
            return {
                phoneme: phoneme,
                viseme_index: visemeIndex,
                start_ms: timing.start_ms,
                end_ms: timing.end_ms,
                duration_ms: timing.end_ms - timing.start_ms
            };
        });
    }
    
    async testSynthesis() {
        const testText = "Hello, this is a test of the text to speech system.";
        
        try {
            const result = await this.synthesize(testText, 1.0);
            console.log('TTS test successful');
            return result;
        } catch (error) {
            console.error('TTS test failed:', error);
            throw error;
        }
    }
    
    async getServerStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`Status request failed: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            throw new Error(`Failed to get server status: ${error.message}`);
        }
    }
    
    async initialize() {
        try {
            await this.checkHealth();
            await this.loadPhonemeMap();
            
            console.log('TTS Controller initialized successfully');
            
        } catch (error) {
            console.error('TTS Controller initialization failed:', error);
            throw error;
        }
    }
    
    validateText(text) {
        const result = {
            valid: true,
            errors: [],
            warnings: []
        };
        
        if (!text || typeof text !== 'string') {
            result.valid = false;
            result.errors.push('Text must be a non-empty string');
            return result;
        }
        
        const trimmedText = text.trim();
        
        if (trimmedText.length === 0) {
            result.valid = false;
            result.errors.push('Text cannot be empty');
            return result;
        }
        
        if (trimmedText.length > 1000) {
            result.valid = false;
            result.errors.push('Text too long (maximum 1000 characters)');
            return result;
        }
        
        if (trimmedText.length > 500) {
            result.warnings.push('Long text may take a while to synthesize');
        }
        
        const unsupportedChars = trimmedText.match(/[^\w\s.,!?;:'"()-]/g);
        if (unsupportedChars) {
            result.warnings.push(`Text contains special characters: ${[...new Set(unsupportedChars)].join('')}`);
        }
        
        return result;
    }
    
    getPhonemeMap() {
        return this.phonemeMap || this.getDefaultPhonemeMap();
    }
    
    isReady() {
        return this.isAvailable && this.phonemeMap !== null;
    }
}