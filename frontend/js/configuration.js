const AVATAR_CONFIGS = {
    highQuality: {
        avatar: {
            useFallbackAvatar: false,
            modelPath: 'assets/models/realistic-avatar.glb',
            texturesPath: 'assets/textures/',
            scale: 1.0,
            position: { x: 0, y: 0, z: 0 },
            enableShadows: true,
            shadowMapSize: 4096,
            enablePostProcessing: true
        },
        animation: {
            expressionBlendSpeed: 0.08,
            visemeBlendSpeed: 0.15,
            emotionDecayRate: 0.95,
            blinkInterval: 3000
        },
        features: {
            eyeTracking: true,
            idleAnimations: true,
            autoEmotions: true,
            contextAwareness: true,
            debugMode: false
        },
        performance: {
            targetFPS: 60,
            adaptiveQuality: true,
            memoryManagement: true
        }
    },
    
    mobile: {
        avatar: {
            useFallbackAvatar: true,
            modelPath: 'assets/models/simple-avatar.glb',
            scale: 1.0,
            position: { x: 0, y: 0, z: 0 },
            enableShadows: false,
            shadowMapSize: 512,
            enablePostProcessing: false
        },
        animation: {
            expressionBlendSpeed: 0.1,
            visemeBlendSpeed: 0.2,
            emotionDecayRate: 0.9,
            blinkInterval: 4000
        },
        features: {
            eyeTracking: false,
            idleAnimations: true,
            autoEmotions: true,
            contextAwareness: true,
            debugMode: false
        },
        performance: {
            targetFPS: 30,
            adaptiveQuality: true,
            memoryManagement: true
        }
    },
    
    development: {
        avatar: {
            useFallbackAvatar: true,
            modelPath: 'assets/models/dev-avatar.glb',
            scale: 1.0,
            position: { x: 0, y: 0, z: 0 },
            enableShadows: true,
            shadowMapSize: 2048,
            enablePostProcessing: false
        },
        animation: {
            expressionBlendSpeed: 0.05, // Slower for debugging
            visemeBlendSpeed: 0.1,
            emotionDecayRate: 0.98,
            blinkInterval: 5000
        },
        features: {
            eyeTracking: true,
            idleAnimations: true,
            autoEmotions: true,
            contextAwareness: true,
            debugMode: true
        },
        performance: {
            targetFPS: 30,
            adaptiveQuality: false,
            memoryManagement: false
        }
    }
};

const DEMO_SCENARIOS = {
    customerService: {
        name: "Customer Service Demo",
        description: "Polite, helpful avatar for customer support",
        config: {
            defaultEmotion: 'neutral',
            emotionIntensity: 0.7,
            contextSensitivity: 0.8
        },
        interactions: [
            {
                trigger: "greeting",
                text: "Hello! How can I help you today?",
                emotion: "happy",
                intensity: 0.6,
                context: "greeting"
            },
            {
                trigger: "problem",
                text: "I understand you're having an issue. Let me help you with that.",
                emotion: "sad",
                intensity: 0.4,
                context: "error"
            },
            {
                trigger: "solution",
                text: "Great! I'm glad we could resolve that for you.",
                emotion: "happy",
                intensity: 0.8,
                context: "success"
            }
        ]
    },
    
    tutor: {
        name: "Educational Tutor Demo",
        description: "Encouraging avatar for learning environments",
        config: {
            defaultEmotion: 'neutral',
            emotionIntensity: 0.8,
            contextSensitivity: 0.9
        },
        interactions: [
            {
                trigger: "lesson_start",
                text: "Welcome to today's lesson! Are you ready to learn something amazing?",
                emotion: "happy",
                intensity: 0.7,
                context: "greeting"
            },
            {
                trigger: "correct_answer",
                text: "Excellent work! You got that exactly right!",
                emotion: "happy",
                intensity: 0.9,
                context: "success"
            },
            {
                trigger: "wrong_answer",
                text: "That's not quite right, but don't worry - let's try again!",
                emotion: "neutral",
                intensity: 0.6,
                context: "error"
            },
            {
                trigger: "explanation",
                text: "Let me explain this concept step by step...",
                emotion: "neutral",
                intensity: 0.5,
                context: "explanation"
            }
        ]
    },
    
    entertainment: {
        name: "Entertainment Presenter Demo",
        description: "Energetic avatar for entertainment content",
        config: {
            defaultEmotion: 'happy',
            emotionIntensity: 0.9,
            contextSensitivity: 0.7
        },
        interactions: [
            {
                trigger: "show_intro",
                text: "Welcome to the show! Get ready for some incredible entertainment!",
                emotion: "happy",
                intensity: 1.0,
                context: "greeting"
            },
            {
                trigger: "surprise_reveal",
                text: "You'll never believe what happens next!",
                emotion: "surprised",
                intensity: 0.9,
                context: "question"
            },
            {
                trigger: "dramatic_moment",
                text: "This is the most incredible thing I've ever seen!",
                emotion: "surprised",
                intensity: 1.0,
                context: "success"
            }
        ]
    }
};

const EXPRESSION_PRESETS = {
    microExpressions: {
        subtle_smile: {
            happy: 0.2,
            duration: 1000
        },
        slight_concern: {
            sad: 0.15,
            eyebrowFrownLeft: 0.3,
            eyebrowFrownRight: 0.3,
            duration: 2000
        },
        mild_confusion: {
            surprised: 0.2,
            eyebrowRaiseLeft: 0.4,
            duration: 1500
        }
    },
    
    complexExpressions: {
        bittersweet: {
            happy: 0.4,
            sad: 0.3,
            duration: 3000
        },
        nervous_excitement: {
            happy: 0.6,
            fearful: 0.3,
            eyeBlinkLeft: 0.2,
            eyeBlinkRight: 0.2,
            duration: 2500
        },
        pleasant_surprise: {
            happy: 0.7,
            surprised: 0.5,
            eyebrowRaiseLeft: 0.6,
            eyebrowRaiseRight: 0.6,
            duration: 2000
        }
    },
    
    contextualExpressions: {
        thinking_deeply: {
            neutral: 0.8,
            eyebrowFrownLeft: 0.2,
            eyebrowFrownRight: 0.2,
            eyeLookDirection: { x: 0.3, y: 0.1 },
            duration: 4000
        },
        listening_intently: {
            neutral: 0.9,
            eyebrowRaiseLeft: 0.1,
            eyebrowRaiseRight: 0.1,
            eyeLookDirection: { x: 0, y: 0 },
            duration: 0
        },
        explaining_carefully: {
            neutral: 0.7,
            happy: 0.2,
            eyebrowRaiseLeft: 0.3,
            eyebrowRaiseRight: 0.3,
            duration: 0
        }
    }
};

/**
 * Avatar Configuration Manager
 * Handles loading and applying different configurations
 */
class AvatarConfigManager {
    constructor(app) {
        this.app = app;
        this.currentConfig = null;
        this.activeScenario = null;
    }
    
    /**
     * Apply a configuration preset
     */
    async applyConfig(configName) {
        const config = AVATAR_CONFIGS[configName];
        if (!config) {
            throw new Error(`Configuration '${configName}' not found`);
        }
        
        this.currentConfig = config;
        
        // Apply avatar settings
        if (this.app.avatarController) {
            Object.assign(this.app.avatarController.modelConfig, config.avatar);
            this.app.avatarController.setAnimationParameters(config.animation);
        }
        
        // Apply feature settings
        if (config.features.eyeTracking !== undefined) {
            this.app.setEyeTracking(config.features.eyeTracking);
        }
        
        if (config.features.idleAnimations !== undefined) {
            this.app.avatarController.setIdleAnimationsEnabled(config.features.idleAnimations);
        }
        
        if (config.features.autoEmotions !== undefined) {
            this.app.emotionSystem.autoDetect = config.features.autoEmotions;
        }
        
        // Apply performance settings
        if (config.performance.adaptiveQuality) {
            this.enableAdaptiveQuality();
        }
        
        console.log(`Applied configuration: ${configName}`);
    }
    
    /**
     * Load and run a demo scenario
     */
    async loadScenario(scenarioName) {
        const scenario = DEMO_SCENARIOS[scenarioName];
        if (!scenario) {
            throw new Error(`Scenario '${scenarioName}' not found`);
        }
        
        this.activeScenario = scenario;
        
        // Apply scenario configuration
        this.app.emotionSystem.intensity = scenario.config.emotionIntensity;
        this.app.triggerEmotion(scenario.config.defaultEmotion, scenario.config.emotionIntensity);
        
        console.log(`Loaded scenario: ${scenario.name}`);
        console.log(scenario.description);
        
        return scenario;
    }
    
    /**
     * Run a scenario interaction
     */
    async runInteraction(trigger) {
        if (!this.activeScenario) {
            throw new Error('No active scenario loaded');
        }
        
        const interaction = this.activeScenario.interactions.find(i => i.trigger === trigger);
        if (!interaction) {
            throw new Error(`Interaction '${trigger}' not found in current scenario`);
        }
        
        // Set context
        this.app.setContext(interaction.context);
        
        // Apply emotion
        this.app.triggerEmotion(interaction.emotion, interaction.intensity);
        
        // Speak the text
        const textInput = document.getElementById('text-input');
        if (textInput) {
            textInput.value = interaction.text;
            
            // Trigger speech
            setTimeout(() => {
                document.getElementById('speak-btn').click();
            }, 500);
        }
        
        console.log(`Running interaction: ${trigger}`);
    }
    
    /**
     * Apply an expression preset
     */
    applyExpressionPreset(category, presetName) {
        const preset = EXPRESSION_PRESETS[category]?.[presetName];
        if (!preset) {
            throw new Error(`Expression preset '${category}.${presetName}' not found`);
        }
        
        // Apply each expression component
        Object.keys(preset).forEach(key => {
            if (key === 'duration') return;
            if (key === 'eyeLookDirection') {
                this.app.avatarController.setEyeLookDirection(
                    preset[key].x, 
                    preset[key].y
                );
                return;
            }
            
            this.app.avatarController.setExpression(key, preset[key]);
        });
        
        // Handle duration
        if (preset.duration > 0) {
            setTimeout(() => {
                this.app.avatarController.resetExpressions();
            }, preset.duration);
        }
        
        console.log(`Applied expression preset: ${category}.${presetName}`);
    }
    
    /**
     * Enable adaptive quality based on performance
     */
    enableAdaptiveQuality() {
        let frameCount = 0;
        let lastTime = performance.now();
        let avgFPS = 60;
        
        const checkPerformance = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                avgFPS = frameCount;
                frameCount = 0;
                lastTime = currentTime;
                
                // Adjust quality based on FPS
                if (avgFPS < 25) {
                    this.adjustQuality('low');
                } else if (avgFPS < 45) {
                    this.adjustQuality('medium');
                } else {
                    this.adjustQuality('high');
                }
            }
            
            requestAnimationFrame(checkPerformance);
        };
        
        checkPerformance();
    }
    
    /**
     * Adjust rendering quality
     */
    adjustQuality(level) {
        if (!this.app.avatarController) return;
        
        const qualitySettings = {
            low: {
                shadowMapSize: 512,
                pixelRatio: 1,
                antialias: false,
                idleAnimations: false
            },
            medium: {
                shadowMapSize: 1024,
                pixelRatio: Math.min(window.devicePixelRatio, 1.5),
                antialias: true,
                idleAnimations: true
            },
            high: {
                shadowMapSize: 2048,
                pixelRatio: Math.min(window.devicePixelRatio, 2),
                antialias: true,
                idleAnimations: true
            }
        };
        
        const settings = qualitySettings[level];
        if (settings) {
            // Apply settings to renderer
            if (this.app.avatarController.renderer) {
                this.app.avatarController.renderer.setPixelRatio(settings.pixelRatio);
            }
            
            // Adjust idle animations
            this.app.avatarController.setIdleAnimationsEnabled(settings.idleAnimations);
            
            console.log(`Quality adjusted to: ${level}`);
        }
    }
    
    /**
     * Get current configuration info
     */
    getConfigInfo() {
        return {
            currentConfig: this.currentConfig,
            activeScenario: this.activeScenario,
            availableConfigs: Object.keys(AVATAR_CONFIGS),
            availableScenarios: Object.keys(DEMO_SCENARIOS),
            expressionPresets: Object.keys(EXPRESSION_PRESETS)
        };
    }
}

/**
 * Demo Controller
 * Provides easy-to-use methods for demonstrating avatar capabilities
 */
class AvatarDemoController {
    constructor(app, configManager) {
        this.app = app;
        this.configManager = configManager;
        this.demoQueue = [];
        this.isRunning = false;
    }
    
    /**
     * Run a quick emotion demo
     */
    async emotionDemo() {
        const emotions = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted'];
        const texts = {
            happy: "I'm so happy to see you!",
            sad: "I'm feeling a bit sad today.",
            angry: "This is really frustrating!",
            surprised: "Wow, that's amazing!",
            fearful: "I'm a bit scared about this.",
            disgusted: "That's absolutely disgusting!"
        };
        
        for (const emotion of emotions) {
            await this.demonstrateEmotion(emotion, texts[emotion]);
            await this.wait(3000);
        }
        
        // Return to neutral
        this.app.triggerEmotion('neutral', 1.0);
    }
    
    /**
     * Demonstrate a specific emotion
     */
    async demonstrateEmotion(emotion, text) {
        console.log(`Demonstrating emotion: ${emotion}`);
        
        // Set the emotion
        this.app.triggerEmotion(emotion, 0.8);
        
        // Update UI
        const textInput = document.getElementById('text-input');
        if (textInput) {
            textInput.value = text;
        }
        
        // Update emotion button states
        document.querySelectorAll('.emotion-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-emotion') === emotion) {
                btn.classList.add('active');
            }
        });
        
        // Speak the text
        if (this.app.isSpeaking) {
            this.app.handleStop();
            await this.wait(500);
        }
        
        setTimeout(() => {
            document.getElementById('speak-btn').click();
        }, 1000);
    }
    
    /**
     * Demo eye tracking capabilities
     */
    async eyeTrackingDemo() {
        if (!this.app.eyeTracking.enabled) {
            this.app.setEyeTracking(true);
        }
        
        console.log('Starting eye tracking demo');
        
        const positions = [
            { x: 0, y: 0, desc: "Center" },
            { x: 0.5, y: 0, desc: "Right" },
            { x: -0.5, y: 0, desc: "Left" },
            { x: 0, y: 0.3, desc: "Up" },
            { x: 0, y: -0.3, desc: "Down" },
            { x: 0.3, y: 0.2, desc: "Up-Right" },
            { x: -0.3, y: -0.2, desc: "Down-Left" }
        ];
        
        for (const pos of positions) {
            console.log(`Looking ${pos.desc}`);
            this.app.avatarController.setEyeLookDirection(pos.x, pos.y);
            await this.wait(1500);
        }
        
        // Return to center
        this.app.avatarController.setEyeLookDirection(0, 0);
    }
    
    /**
     * Demo complex expressions
     */
    async complexExpressionDemo() {
        const presets = Object.keys(EXPRESSION_PRESETS.complexExpressions);
        
        for (const preset of presets) {
            console.log(`Demonstrating complex expression: ${preset}`);
            this.configManager.applyExpressionPreset('complexExpressions', preset);
            await this.wait(3000);
        }
        
        // Reset
        this.app.avatarController.resetExpressions();
    }
    
    /**
     * Run a full capabilities demo
     */
    async fullDemo() {
        console.log('Starting full avatar capabilities demo');
        
        // 1. Basic emotions
        console.log('Phase 1: Basic Emotions');
        await this.emotionDemo();
        
        await this.wait(2000);
        
        // 2. Eye tracking
        console.log('Phase 2: Eye Tracking');
        await this.eyeTrackingDemo();
        
        await this.wait(2000);
        
        // 3. Complex expressions
        console.log('Phase 3: Complex Expressions');
        await this.complexExpressionDemo();
        
        await this.wait(2000);
        
        // 4. Context scenarios
        console.log('Phase 4: Context Scenarios');
        await this.configManager.loadScenario('customerService');
        await this.configManager.runInteraction('greeting');
        
        await this.wait(4000);
        
        await this.configManager.runInteraction('problem');
        
        await this.wait(4000);
        
        await this.configManager.runInteraction('solution');
        
        console.log('Full demo complete!');
    }
    
    /**
     * Utility method to wait
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for use in main application
export { 
    AVATAR_CONFIGS, 
    DEMO_SCENARIOS, 
    EXPRESSION_PRESETS, 
    AvatarConfigManager, 
    AvatarDemoController 
};

// Usage example:
/*
// Initialize in your main application
import { AvatarConfigManager, AvatarDemoController } from './AvatarConfiguration.js';

// After app initialization
const configManager = new AvatarConfigManager(app);
const demoController = new AvatarDemoController(app, configManager);

// Apply a configuration
await configManager.applyConfig('highQuality');

// Load and run a scenario
await configManager.loadScenario('customerService');
await configManager.runInteraction('greeting');

// Run demonstrations
await demoController.emotionDemo();
await demoController.eyeTrackingDemo();
await demoController.fullDemo();

// Apply expression presets
configManager.applyExpressionPreset('microExpressions', 'subtle_smile');
configManager.applyExpressionPreset('complexExpressions', 'pleasant_surprise');

// Global access for console testing
window.avatarConfig = configManager;
window.avatarDemo = demoController;
*/