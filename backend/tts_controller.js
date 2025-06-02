/**
 * TTS Controller
 * Handles communication with the local TTS server for speech synthesis
 */

export class TTSController {
    /**
     * Initialize the TTS Controller
     * @param {string} serverUrl - URL of the local TTS server
     */
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.phonemeMap = null;
        this.isAvailable = false;
        
        // Request timeout settings
        this.healthTimeout = 5000; // 5 seconds for health check
        this.synthesisTimeout = 30000; // 30 seconds for synthesis
    }
    
    /**
     * Check if the TTS server is healthy and responsive
     * @returns {Promise<boolean>} True if server is available
     */
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
    
    /**
     * Load the phoneme to viseme mapping from the server
     * @returns {Promise<Object>} Phoneme mapping object
     */
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
            
            // Fallback to default phoneme mapping
            this.phonemeMap = this.getDefaultPhonemeMap();
            return this.phonemeMap;
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
     * Synthesize speech from text
     * @param {string} text - Text to synthesize
     * @param {number} speed - Speech speed multiplier (default: 1.0)
     * @returns {Promise<Object>} Synthesis result with audio data and phoneme timings
     */
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
            
            // Validate response format
            if (!result.audio_data || !result.phoneme_timings) {
                throw new Error('Invalid response format from TTS server');
            }
            
            // Process phoneme timings to include viseme indices
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
    
    /**
     * Process phoneme timings to include viseme indices
     * @param {Array} timings - Raw phoneme timings from TTS
     * @returns {Array} Processed timings with viseme indices
     */
    processPhonemeTimings(timings) {
        if (!this.phonemeMap) {
            console.warn('No phoneme map available, using default');
            this.phonemeMap = this.getDefaultPhonemeMap();
        }
        
        return timings.map(timing => {
            const phoneme = timing.phoneme.toUpperCase();
            const visemeIndex = this.phonemeMap[phoneme] !== undefined 
                ? this.phonemeMap[phoneme] 
                : this.phonemeMap['SIL']; // Default to silence
            
            return {
                phoneme: phoneme,
                viseme_index: visemeIndex,
                start_ms: timing.start_ms,
                end_ms: timing.end_ms,
                duration_ms: timing.end_ms - timing.start_ms
            };
        });
    }
    
    /**
     * Test the TTS system with a simple phrase
     * @returns {Promise<Object>} Test synthesis result
     */
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
    
    /**
     * Get server status information
     * @returns {Promise<Object>} Server status
     */
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
    
    /**
     * Initialize the TTS controller
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            // Check server health
            await this.checkHealth();
            
            // Load phoneme mapping
            await this.loadPhonemeMap();
            
            console.log('TTS Controller initialized successfully');
            
        } catch (error) {
            console.error('TTS Controller initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Validate text input for synthesis
     * @param {string} text - Text to validate
     * @returns {Object} Validation result
     */
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
        
        // Check for unsupported characters
        const unsupportedChars = trimmedText.match(/[^\w\s.,!?;:'"()-]/g);
        if (unsupportedChars) {
            result.warnings.push(`Text contains special characters: ${[...new Set(unsupportedChars)].join('')}`);
        }
        
        return result;
    }
    
    /**
     * Get the phoneme to viseme mapping
     * @returns {Object} Phoneme mapping
     */
    getPhonemeMap() {
        return this.phonemeMap || this.getDefaultPhonemeMap();
    }
    
    /**
     * Check if the TTS controller is ready for synthesis
     * @returns {boolean} True if ready
     */
    isReady() {
        return this.isAvailable && this.phonemeMap !== null;
    }
}
