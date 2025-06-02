/**
 * Avatar Controller
 * Handles 3D avatar loading, rendering, and blend shape animations using Three.js
 */

export class AvatarController {
    /**
     * Initialize the Avatar Controller
     * @param {string} canvasId - ID of the canvas element for rendering
     */
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.canvas = null;
        
        // Three.js components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // Avatar model
        this.avatarModel = null;
        this.avatarMesh = null;
        this.blendShapes = new Map();
        this.morphTargets = {};
        
        // Animation state
        this.isAnimating = false;
        this.idleAnimation = {
            time: 0,
            breathingIntensity: 0.02,
            headSwayIntensity: 0.01
        };
        
        // Viseme weights for lip sync
        this.visemeWeights = new Array(14).fill(0);
        this.targetVisemeWeights = new Array(14).fill(0);
        this.visemeBlendSpeed = 0.15;
        
        // Bind methods
        this.animate = this.animate.bind(this);
        this.onWindowResize = this.onWindowResize.bind(this);
    }
    
    /**
     * Initialize the 3D scene and load the avatar
     */
    async initialize() {
        try {
            // Get canvas element
            this.canvas = document.getElementById(this.canvasId);
            if (!this.canvas) {
                throw new Error(`Canvas element '${this.canvasId}' not found`);
            }
            
            // Setup Three.js scene
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupLights();
            this.setupControls();
            
            // Load avatar model
            await this.loadAvatar();
            
            // Setup window resize handler
            window.addEventListener('resize', this.onWindowResize);
            
            // Start animation loop
            this.startAnimation();
            
        } catch (error) {
            console.error('Failed to initialize Avatar Controller:', error);
            throw error;
        }
    }
    
    /**
     * Setup the Three.js scene
     */
    setupScene() {
        this.scene = new THREE.Scene();
        
        // Set background to transparent for better integration
        this.scene.background = null;
        
        // Add fog for depth
        this.scene.fog = new THREE.Fog(0x222222, 10, 50);
    }
    
    /**
     * Setup the camera
     */
    setupCamera() {
        const aspect = this.canvas.clientWidth / this.canvas.clientHeight;
        this.camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 100);
        
        // Position camera to frame head and shoulders
        this.camera.position.set(0, 1.6, 3);
        this.camera.lookAt(0, 1.6, 0);
    }
    
    /**
     * Setup the WebGL renderer
     */
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true
        });
        
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Enable shadows
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Enable physically based rendering
        this.renderer.physicallyCorrectLights = true;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
    }
    
    /**
     * Setup lighting for realistic appearance
     */
    setupLights() {
        // Key light (main illumination)
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
        keyLight.position.set(2, 4, 3);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        keyLight.shadow.camera.near = 0.5;
        keyLight.shadow.camera.far = 50;
        keyLight.shadow.bias = -0.0001;
        this.scene.add(keyLight);
        
        // Fill light (soften shadows)
        const fillLight = new THREE.DirectionalLight(0x8bb4ff, 0.4);
        fillLight.position.set(-2, 2, 1);
        this.scene.add(fillLight);
        
        // Rim light (edge definition)
        const rimLight = new THREE.DirectionalLight(0xffffff, 0.6);
        rimLight.position.set(0, 2, -3);
        this.scene.add(rimLight);
        
        // Ambient light (general illumination)
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);
        
        // Environment light (for realistic reflections)
        const envLight = new THREE.HemisphereLight(0x87ceeb, 0x362f1a, 0.4);
        this.scene.add(envLight);
    }
    
    /**
     * Setup camera controls
     */
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.enableZoom = true;
        this.controls.enablePan = false;
        this.controls.maxPolarAngle = Math.PI / 2;
        this.controls.minDistance = 1.5;
        this.controls.maxDistance = 8;
        this.controls.target.set(0, 1.6, 0);
    }
    
    /**
     * Load the avatar model
     * For this demo, we'll create a simple procedural avatar
     * In production, you'd load a real glTF model with blend shapes
     */
    async loadAvatar() {
        // Create a simple avatar using basic geometry
        // In a real implementation, use GLTFLoader to load a proper avatar model
        await this.createProceduralAvatar();
        
        // Setup blend shapes for lip sync
        this.setupBlendShapes();
    }
    
    /**
     * Create a simple procedural avatar for demonstration
     * In production, replace this with GLTFLoader to load a real avatar model
     */
    async createProceduralAvatar() {
        const avatarGroup = new THREE.Group();
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.35, 32, 32);
        const headMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xfdbcb4,
            roughness: 0.8,
            metalness: 0.0,
            clearcoat: 0.1
        });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.7;
        head.castShadow = true;
        head.receiveShadow = true;
        avatarGroup.add(head);
        
        // Eyes
        const eyeGeometry = new THREE.SphereGeometry(0.08, 16, 16);
        const eyeMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x2c5f2d,
            roughness: 0.1,
            metalness: 0.0
        });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.12, 1.75, 0.25);
        avatarGroup.add(leftEye);
        
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.12, 1.75, 0.25);
        avatarGroup.add(rightEye);
        
        // Mouth area (this will be animated for lip sync)
        const mouthGeometry = new THREE.SphereGeometry(0.08, 16, 16);
        const mouthMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xc97b7b,
            roughness: 0.9,
            metalness: 0.0
        });
        
        this.mouthMesh = new THREE.Mesh(mouthGeometry, mouthMaterial);
        this.mouthMesh.position.set(0, 1.6, 0.3);
        this.mouthMesh.scale.set(1, 0.3, 0.8);
        avatarGroup.add(this.mouthMesh);
        
        // Hair
        const hairGeometry = new THREE.SphereGeometry(0.38, 16, 16);
        const hairMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x8b4513,
            roughness: 0.95,
            metalness: 0.0
        });
        const hair = new THREE.Mesh(hairGeometry, hairMaterial);
        hair.position.y = 1.85;
        hair.scale.set(1, 0.8, 1);
        avatarGroup.add(hair);
        
        // Neck
        const neckGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.3, 16);
        const neckMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xfdbcb4,
            roughness: 0.8,
            metalness: 0.0
        });
        const neck = new THREE.Mesh(neckGeometry, neckMaterial);
        neck.position.y = 1.35;
        neck.castShadow = true;
        avatarGroup.add(neck);
        
        // Shoulders
        const shoulderGeometry = new THREE.BoxGeometry(0.8, 0.3, 0.4);
        const shoulderMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x4a90e2,
            roughness: 0.7,
            metalness: 0.0
        });
        const shoulders = new THREE.Mesh(shoulderGeometry, shoulderMaterial);
        shoulders.position.y = 1.0;
        shoulders.castShadow = true;
        avatarGroup.add(shoulders);
        
        this.avatarModel = avatarGroup;
        this.avatarMesh = head; // Main mesh for animations
        this.scene.add(avatarGroup);
    }
    
    /**
     * Setup blend shapes for lip sync animation
     * Maps viseme indices to mouth shape transformations
     */
    setupBlendShapes() {
        // Define mouth shapes for different visemes
        // Each viseme has scale and position transformations
        this.visemeShapes = {
            0: { scaleY: 0.8, scaleX: 1.2, posZ: 0.32 }, // AH, AA (open)
            1: { scaleY: 0.4, scaleX: 0.8, posZ: 0.35 }, // AO, OW (rounded)
            2: { scaleY: 0.6, scaleX: 1.1, posZ: 0.31 }, // EH, ER, EY (mid)
            3: { scaleY: 0.3, scaleX: 1.4, posZ: 0.29 }, // IH, IY (wide)
            4: { scaleY: 0.4, scaleX: 0.7, posZ: 0.35 }, // UH, UW (tight)
            5: { scaleY: 0.2, scaleX: 0.6, posZ: 0.28 }, // B, P, M (closed)
            6: { scaleY: 0.4, scaleX: 1.0, posZ: 0.32 }, // F, V (teeth on lip)
            7: { scaleY: 0.3, scaleX: 1.2, posZ: 0.30 }, // TH, DH (tongue)
            8: { scaleY: 0.5, scaleX: 1.0, posZ: 0.31 }, // T, D, N, L, R
            9: { scaleY: 0.3, scaleX: 1.1, posZ: 0.30 }, // S, Z (sibilant)
            10: { scaleY: 0.4, scaleX: 0.9, posZ: 0.32 }, // SH, ZH, CH, JH
            11: { scaleY: 0.6, scaleX: 1.0, posZ: 0.31 }, // K, G, NG
            12: { scaleY: 0.5, scaleX: 1.0, posZ: 0.31 }, // HH, Y, W
            13: { scaleY: 0.3, scaleX: 1.0, posZ: 0.30 }  // SIL (neutral)
        };
        
        // Initialize current shape
        this.currentMouthShape = { scaleY: 0.3, scaleX: 1.0, posZ: 0.30 };
    }
    
    /**
     * Set the weight of a specific viseme blend shape
     * @param {number} visemeIndex - Index of the viseme (0-13)
     * @param {number} weight - Weight of the blend shape (0.0-1.0)
     */
    setViseme(visemeIndex, weight) {
        if (visemeIndex >= 0 && visemeIndex < this.targetVisemeWeights.length) {
            this.targetVisemeWeights[visemeIndex] = Math.max(0, Math.min(1, weight));
        }
    }
    
    /**
     * Update the avatar animation
     * @param {number} deltaTime - Time elapsed since last frame (seconds)
     */
    update(deltaTime) {
        if (!this.avatarModel) return;
        
        // Update idle animation
        this.updateIdleAnimation(deltaTime);
        
        // Update viseme blending
        this.updateVisemeBlending(deltaTime);
        
        // Update mouth shape based on current viseme weights
        this.updateMouthShape();
        
        // Update camera controls
        if (this.controls) {
            this.controls.update();
        }
    }
    
    /**
     * Update idle animation (breathing, subtle movement)
     * @param {number} deltaTime - Time elapsed since last frame
     */
    updateIdleAnimation(deltaTime) {
        this.idleAnimation.time += deltaTime;
        
        if (this.avatarMesh) {
            // Subtle breathing animation
            const breathScale = 1 + Math.sin(this.idleAnimation.time * 1.5) * this.idleAnimation.breathingIntensity;
            this.avatarModel.scale.y = breathScale;
            
            // Gentle head sway
            const swayAngle = Math.sin(this.idleAnimation.time * 0.8) * this.idleAnimation.headSwayIntensity;
            this.avatarMesh.rotation.z = swayAngle;
        }
    }
    
    /**
     * Update viseme weight blending for smooth transitions
     * @param {number} deltaTime - Time elapsed since last frame
     */
    updateVisemeBlending(deltaTime) {
        for (let i = 0; i < this.visemeWeights.length; i++) {
            const target = this.targetVisemeWeights[i];
            const current = this.visemeWeights[i];
            const diff = target - current;
            
            // Smooth interpolation
            this.visemeWeights[i] += diff * this.visemeBlendSpeed;
            
            // Clamp to prevent overshoot
            if (Math.abs(diff) < 0.001) {
                this.visemeWeights[i] = target;
            }
        }
    }
    
    /**
     * Update mouth shape based on current viseme weights
     */
    updateMouthShape() {
        if (!this.mouthMesh) return;
        
        // Find the dominant viseme
        let maxWeight = 0;
        let dominantViseme = 13; // Default to neutral
        
        for (let i = 0; i < this.visemeWeights.length; i++) {
            if (this.visemeWeights[i] > maxWeight) {
                maxWeight = this.visemeWeights[i];
                dominantViseme = i;
            }
        }
        
        // Blend to target shape
        const targetShape = this.visemeShapes[dominantViseme];
        if (targetShape) {
            const blendFactor = 0.1;
            
            this.currentMouthShape.scaleY += (targetShape.scaleY - this.currentMouthShape.scaleY) * blendFactor;
            this.currentMouthShape.scaleX += (targetShape.scaleX - this.currentMouthShape.scaleX) * blendFactor;
            this.currentMouthShape.posZ += (targetShape.posZ - this.currentMouthShape.posZ) * blendFactor;
            
            // Apply transformations
            this.mouthMesh.scale.y = this.currentMouthShape.scaleY;
            this.mouthMesh.scale.x = this.currentMouthShape.scaleX;
            this.mouthMesh.position.z = this.currentMouthShape.posZ;
        }
    }
    
    /**
     * Start the animation loop
     */
    startAnimation() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        this.lastFrameTime = performance.now();
        this.animate();
    }
    
    /**
     * Stop the animation loop
     */
    stopAnimation() {
        this.isAnimating = false;
    }
    
    /**
     * Animation loop
     */
    animate() {
        if (!this.isAnimating) return;
        
        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastFrameTime) / 1000;
        this.lastFrameTime = currentTime;
        
        // Update avatar
        this.update(deltaTime);
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
        
        // Continue animation loop
        requestAnimationFrame(this.animate);
    }
    
    /**
     * Handle window resize
     */
    onWindowResize() {
        if (!this.camera || !this.renderer || !this.canvas) return;
        
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    /**
     * Reset all viseme weights to neutral
     */
    resetVisemes() {
        this.targetVisemeWeights.fill(0);
        this.targetVisemeWeights[13] = 1; // Set neutral position
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        this.stopAnimation();
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        window.removeEventListener('resize', this.onWindowResize);
    }
}
