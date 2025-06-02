/**
 * Avatar Controller with Realistic 3D Models and Facial Expressions
 * Supports glTF models, comprehensive facial expressions, and emotion systems
 */

export class AvatarController {
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.canvas = null;
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.clock = new THREE.Clock();
        
        this.gltfLoader = new THREE.GLTFLoader();
        this.textureLoader = new THREE.TextureLoader();
        
        this.avatarModel = null;
        this.avatarMesh = null;
        this.avatarMixer = null;
        this.morphTargets = new Map();
        this.morphInfluences = {};
        
        this.expressions = {
            happy: { intensity: 0, target: 0 },
            sad: { intensity: 0, target: 0 },
            angry: { intensity: 0, target: 0 },
            surprised: { intensity: 0, target: 0 },
            disgusted: { intensity: 0, target: 0 },
            fearful: { intensity: 0, target: 0 },
            neutral: { intensity: 1, target: 1 },
            
            eyeBlinkLeft: { intensity: 0, target: 0 },
            eyeBlinkRight: { intensity: 0, target: 0 },
            eyebrowRaiseLeft: { intensity: 0, target: 0 },
            eyebrowRaiseRight: { intensity: 0, target: 0 },
            eyebrowFrownLeft: { intensity: 0, target: 0 },
            eyebrowFrownRight: { intensity: 0, target: 0 },
            cheekPuffLeft: { intensity: 0, target: 0 },
            cheekPuffRight: { intensity: 0, target: 0 },
            
            eyeLeftUp: { intensity: 0, target: 0 },
            eyeLeftDown: { intensity: 0, target: 0 },
            eyeLeftLeft: { intensity: 0, target: 0 },
            eyeLeftRight: { intensity: 0, target: 0 },
            eyeRightUp: { intensity: 0, target: 0 },
            eyeRightDown: { intensity: 0, target: 0 },
            eyeRightLeft: { intensity: 0, target: 0 },
            eyeRightRight: { intensity: 0, target: 0 }
        };
        
        this.visemeWeights = new Array(14).fill(0);
        this.targetVisemeWeights = new Array(14).fill(0);
        this.visemeBlendSpeed = 0.15;
        
        this.isAnimating = false;
        this.animationMixers = [];
        this.currentAnimations = new Map();
        
        this.idleSystem = {
            enabled: true,
            blinkTimer: 0,
            blinkInterval: 3000,
            lastBlinkTime: 0,
            breathingTime: 0,
            breathingIntensity: 0.02,
            headMovementTime: 0,
            eyeMovementTime: 0,
            microExpressionTime: 0
        };
        
        this.expressionBlendSpeed = 0.08;
        this.emotionDecayRate = 0.95;
        
        this.modelConfig = {
            useFallbackAvatar: true,
            modelPath: 'assets/models/avatar.glb',
            texturesPath: 'assets/textures/',
            scale: 1.0,
            position: { x: 0, y: 0, z: 0 },
            enableShadows: true
        };
        
        this.animate = this.animate.bind(this);
        this.onWindowResize = this.onWindowResize.bind(this);
        this.onProgress = this.onProgress.bind(this);
        this.onError = this.onError.bind(this);
    }
    
    async initialize() {
        try {
            this.canvas = document.getElementById(this.canvasId);
            if (!this.canvas) {
                throw new Error(`Canvas element '${this.canvasId}' not found`);
            }
            
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupLights();
            this.setupControls();
            this.setupPostProcessing();
            
            await this.loadAvatar();
            
            window.addEventListener('resize', this.onWindowResize);
            
            this.startAnimation();
            
            console.log('Avatar Controller initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize Avatar Controller:', error);
            throw error;
        }
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.setupEnvironment();
        this.scene.fog = new THREE.Fog(0x263238, 8, 25);
    }
    
    setupEnvironment() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        const gradient = ctx.createLinearGradient(0, 0, 0, 512);
        gradient.addColorStop(0, '#87CEEB');
        gradient.addColorStop(1, '#E0F6FF');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 512, 512);
        
        const backgroundTexture = new THREE.CanvasTexture(canvas);
        this.scene.background = backgroundTexture;
    }
    
    setupCamera() {
        const aspect = this.canvas.clientWidth / this.canvas.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
        
        this.camera.position.set(0, 1.65, 2.5);
        this.camera.lookAt(0, 1.6, 0);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.physicallyCorrectLights = true;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.0;
        
        this.renderer.gammaFactor = 2.2;
    }
    
    setupLights() {
        const keyLight = new THREE.DirectionalLight(0xffeedd, 1.5);
        keyLight.position.set(3, 6, 4);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 4096;
        keyLight.shadow.mapSize.height = 4096;
        keyLight.shadow.camera.near = 0.5;
        keyLight.shadow.camera.far = 20;
        keyLight.shadow.camera.left = -5;
        keyLight.shadow.camera.right = 5;
        keyLight.shadow.camera.top = 5;
        keyLight.shadow.camera.bottom = -5;
        keyLight.shadow.bias = -0.0005;
        this.scene.add(keyLight);
        
        const fillLight = new THREE.DirectionalLight(0xaaccff, 0.6);
        fillLight.position.set(-3, 3, 2);
        this.scene.add(fillLight);
        
        const rimLight = new THREE.DirectionalLight(0xffddaa, 0.8);
        rimLight.position.set(0, 3, -4);
        this.scene.add(rimLight);
        
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        const faceLight = new THREE.PointLight(0xffeedd, 0.5, 10);
        faceLight.position.set(0, 1.8, 1.5);
        this.scene.add(faceLight);
        
        const hairLight = new THREE.SpotLight(0xffffff, 0.7, 10, Math.PI / 6, 0.5);
        hairLight.position.set(0, 4, -2);
        hairLight.target.position.set(0, 2, 0);
        this.scene.add(hairLight);
        this.scene.add(hairLight.target);
    }
    
    setupPostProcessing() {
        // Post-processing can be added here for effects
    }
    
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.enableZoom = true;
        this.controls.enablePan = true;
        this.controls.maxPolarAngle = Math.PI * 0.7;
        this.controls.minPolarAngle = Math.PI * 0.2;
        this.controls.minDistance = 1.5;
        this.controls.maxDistance = 10;
        this.controls.target.set(0, 1.6, 0);
        
        this.controls.zoomSpeed = 0.5;
        this.controls.panSpeed = 0.8;
        this.controls.rotateSpeed = 0.5;
    }
    
    async loadAvatar() {
        try {
            await this.loadGLTFAvatar();
        } catch (error) {
            console.warn('Failed to load glTF avatar, using fallback:', error);
            
            if (this.modelConfig.useFallbackAvatar) {
                await this.createProceduralAvatar();
            } else {
                throw error;
            }
        }
        
        this.setupFacialExpressionSystem();
        this.setupIdleAnimations();
    }
    
    async loadGLTFAvatar() {
        return new Promise((resolve, reject) => {
            this.gltfLoader.load(
                this.modelConfig.modelPath,
                (gltf) => this.onGLTFLoaded(gltf, resolve),
                this.onProgress,
                (error) => this.onError(error, reject)
            );
        });
    }
    
    onGLTFLoaded(gltf, resolve) {
        console.log('glTF model loaded successfully');
        
        this.avatarModel = gltf.scene;
        this.avatarModel.scale.setScalar(this.modelConfig.scale);
        this.avatarModel.position.set(
            this.modelConfig.position.x,
            this.modelConfig.position.y,
            this.modelConfig.position.z
        );
        
        this.avatarModel.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = this.modelConfig.enableShadows;
                child.receiveShadow = this.modelConfig.enableShadows;
                
                if (child.name.toLowerCase().includes('head') || 
                    child.name.toLowerCase().includes('face')) {
                    this.avatarMesh = child;
                }
                
                if (child.material) {
                    this.enhanceMaterial(child.material);
                }
            }
        });
        
        if (gltf.animations && gltf.animations.length > 0) {
            this.avatarMixer = new THREE.AnimationMixer(this.avatarModel);
            
            gltf.animations.forEach((clip) => {
                const action = this.avatarMixer.clipAction(clip);
                this.currentAnimations.set(clip.name, action);
            });
        }
        
        this.scene.add(this.avatarModel);
        this.extractMorphTargets();
        
        resolve();
    }
    
    extractMorphTargets() {
        if (!this.avatarMesh || !this.avatarMesh.morphTargetDictionary) {
            console.warn('No morph targets found in avatar model');
            return;
        }
        
        const morphDict = this.avatarMesh.morphTargetDictionary;
        
        const expressionMapping = {
            'happy': 'happy',
            'smile': 'happy',
            'joy': 'happy',
            'sad': 'sad',
            'frown': 'sad',
            'angry': 'angry',
            'mad': 'angry',
            'surprised': 'surprised',
            'shock': 'surprised',
            'fear': 'fearful',
            'disgust': 'disgusted',
            
            'eyeBlinkLeft': 'eyeBlinkLeft',
            'eyeBlinkRight': 'eyeBlinkRight',
            'browUpLeft': 'eyebrowRaiseLeft',
            'browUpRight': 'eyebrowRaiseRight',
            'browDownLeft': 'eyebrowFrownLeft',
            'browDownRight': 'eyebrowFrownRight',
            
            'viseme_AA': 0, 'viseme_AH': 0,
            'viseme_AO': 1, 'viseme_OW': 1,
            'viseme_EH': 2, 'viseme_ER': 2,
            'viseme_IH': 3, 'viseme_IY': 3,
            'viseme_UH': 4, 'viseme_UW': 4,
            'viseme_B': 5, 'viseme_P': 5, 'viseme_M': 5,
            'viseme_F': 6, 'viseme_V': 6,
            'viseme_TH': 7, 'viseme_DH': 7,
            'viseme_T': 8, 'viseme_D': 8, 'viseme_N': 8,
            'viseme_S': 9, 'viseme_Z': 9,
            'viseme_SH': 10, 'viseme_CH': 10,
            'viseme_K': 11, 'viseme_G': 11,
            'viseme_HH': 12, 'viseme_Y': 12,
            'viseme_SIL': 13
        };
        
        Object.keys(morphDict).forEach(morphName => {
            const morphIndex = morphDict[morphName];
            const mappedName = expressionMapping[morphName];
            
            if (mappedName !== undefined) {
                if (typeof mappedName === 'string') {
                    this.morphTargets.set(mappedName, morphIndex);
                } else {
                    this.morphTargets.set(`viseme_${mappedName}`, morphIndex);
                }
            }
        });
        
        console.log('Mapped morph targets:', this.morphTargets.size);
    }
    
    enhanceMaterial(material) {
        if (material.isMeshStandardMaterial || material.isMeshPhysicalMaterial) {
            if (material.name && material.name.toLowerCase().includes('skin')) {
                material.roughness = 0.8;
                material.metalness = 0.0;
                material.transparent = false;
                
                if (material.isMeshPhysicalMaterial) {
                    material.transmission = 0.1;
                    material.thickness = 0.5;
                }
            }
            
            if (material.name && material.name.toLowerCase().includes('eye')) {
                material.roughness = 0.1;
                material.metalness = 0.0;
                material.transparent = true;
                material.opacity = 0.95;
            }
            
            if (material.name && material.name.toLowerCase().includes('hair')) {
                material.roughness = 0.9;
                material.metalness = 0.1;
            }
        }
    }
    
    async createProceduralAvatar() {
        console.log('Creating procedural avatar');
        
        const avatarGroup = new THREE.Group();
        
        const headGeometry = this.createDetailedHeadGeometry();
        const headMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xfdbcb4,
            roughness: 0.8,
            metalness: 0.0,
            clearcoat: 0.1,
            clearcoatRoughness: 0.1
        });
        
        this.avatarMesh = new THREE.Mesh(headGeometry, headMaterial);
        this.avatarMesh.position.y = 1.7;
        this.avatarMesh.castShadow = true;
        this.avatarMesh.receiveShadow = true;
        avatarGroup.add(this.avatarMesh);
        
        this.createDetailedEyes(avatarGroup);
        this.createDetailedMouth(avatarGroup);
        this.createDetailedHair(avatarGroup);
        this.createDetailedBody(avatarGroup);
        
        this.avatarModel = avatarGroup;
        this.scene.add(avatarGroup);
        
        this.setupProceduralMorphTargets();
    }
    
    createDetailedHeadGeometry() {
        const geometry = new THREE.SphereGeometry(0.35, 64, 64);
        
        const positions = geometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i);
            const y = positions.getY(i);
            const z = positions.getZ(i);
            
            if (z < -0.2) {
                positions.setZ(i, z * 0.7);
            }
            
            if (z > 0.2) {
                positions.setZ(i, z * 0.9);
            }
            
            if (y > 0.2) {
                positions.setX(i, x * 0.95);
            }
        }
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
        
        return geometry;
    }
    
    createDetailedEyes(parentGroup) {
        const socketGeometry = new THREE.SphereGeometry(0.1, 32, 32);
        const socketMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xe8c8b8,
            roughness: 0.9,
            metalness: 0.0
        });
        
        const eyeGeometry = new THREE.SphereGeometry(0.08, 32, 32);
        const eyeMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xffffff,
            roughness: 0.1,
            metalness: 0.0,
            transparent: true,
            opacity: 0.95
        });
        
        const irisGeometry = new THREE.SphereGeometry(0.04, 32, 32);
        const irisMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x2c5f2d,
            roughness: 0.3,
            metalness: 0.0
        });
        
        const leftEyeGroup = new THREE.Group();
        const leftSocket = new THREE.Mesh(socketGeometry, socketMaterial);
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        const leftIris = new THREE.Mesh(irisGeometry, irisMaterial);
        
        leftIris.position.z = 0.04;
        leftEye.add(leftIris);
        leftSocket.add(leftEye);
        leftEyeGroup.add(leftSocket);
        leftEyeGroup.position.set(-0.12, 1.75, 0.25);
        
        const rightEyeGroup = new THREE.Group();
        const rightSocket = new THREE.Mesh(socketGeometry, socketMaterial);
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        const rightIris = new THREE.Mesh(irisGeometry, irisMaterial);
        
        rightIris.position.z = 0.04;
        rightEye.add(rightIris);
        rightSocket.add(rightEye);
        rightEyeGroup.add(rightSocket);
        rightEyeGroup.position.set(0.12, 1.75, 0.25);
        
        parentGroup.add(leftEyeGroup);
        parentGroup.add(rightEyeGroup);
        
        this.leftEye = leftEyeGroup;
        this.rightEye = rightEyeGroup;
        this.leftEyeBall = leftEye;
        this.rightEyeBall = rightEye;
    }
    
    createDetailedMouth(parentGroup) {
        const upperLipGeometry = new THREE.SphereGeometry(0.06, 32, 16);
        const lipMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xc97b7b,
            roughness: 0.8,
            metalness: 0.0
        });
        
        this.upperLip = new THREE.Mesh(upperLipGeometry, lipMaterial);
        this.upperLip.position.set(0, 1.63, 0.32);
        this.upperLip.scale.set(1.2, 0.4, 0.8);
        parentGroup.add(this.upperLip);
        
        const lowerLipGeometry = new THREE.SphereGeometry(0.05, 32, 16);
        this.lowerLip = new THREE.Mesh(lowerLipGeometry, lipMaterial);
        this.lowerLip.position.set(0, 1.57, 0.32);
        this.lowerLip.scale.set(1.1, 0.4, 0.8);
        parentGroup.add(this.lowerLip);
        
        const teethGeometry = new THREE.BoxGeometry(0.12, 0.02, 0.02);
        const teethMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xffffff,
            roughness: 0.1,
            metalness: 0.0
        });
        
        this.teeth = new THREE.Mesh(teethGeometry, teethMaterial);
        this.teeth.position.set(0, 1.6, 0.33);
        this.teeth.visible = false;
        parentGroup.add(this.teeth);
        
        const tongueGeometry = new THREE.SphereGeometry(0.04, 32, 16);
        const tongueMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xff6b6b,
            roughness: 0.9,
            metalness: 0.0
        });
        
        this.tongue = new THREE.Mesh(tongueGeometry, tongueMaterial);
        this.tongue.position.set(0, 1.58, 0.28);
        this.tongue.scale.set(1.5, 0.8, 1.2);
        this.tongue.visible = false;
        parentGroup.add(this.tongue);
    }
    
    createDetailedHair(parentGroup) {
        const hairGeometry = new THREE.SphereGeometry(0.38, 32, 32);
        const hairMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x8b4513,
            roughness: 0.95,
            metalness: 0.1,
            transparent: true,
            opacity: 0.9
        });
        
        const hair = new THREE.Mesh(hairGeometry, hairMaterial);
        hair.position.y = 1.85;
        hair.scale.set(1, 0.8, 1);
        parentGroup.add(hair);
        
        for (let i = 0; i < 20; i++) {
            const strandGeometry = new THREE.CylinderGeometry(0.002, 0.001, 0.3, 8);
            const strand = new THREE.Mesh(strandGeometry, hairMaterial);
            
            const angle = (i / 20) * Math.PI * 2;
            const radius = 0.35 + Math.random() * 0.05;
            strand.position.set(
                Math.cos(angle) * radius,
                1.9 + Math.random() * 0.2,
                Math.sin(angle) * radius
            );
            strand.rotation.z = (Math.random() - 0.5) * 0.3;
            strand.rotation.x = (Math.random() - 0.5) * 0.2;
            
            parentGroup.add(strand);
        }
    }
    
    createDetailedBody(parentGroup) {
        const neckGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.3, 32);
        const skinMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xfdbcb4,
            roughness: 0.8,
            metalness: 0.0
        });
        
        const neck = new THREE.Mesh(neckGeometry, skinMaterial);
        neck.position.y = 1.35;
        neck.castShadow = true;
        parentGroup.add(neck);
        
        const shoulderGeometry = new THREE.BoxGeometry(0.8, 0.3, 0.4);
        const clothingMaterial = new THREE.MeshPhysicalMaterial({
            color: 0x4a90e2,
            roughness: 0.7,
            metalness: 0.0
        });
        
        const shoulders = new THREE.Mesh(shoulderGeometry, clothingMaterial);
        shoulders.position.y = 1.0;
        shoulders.castShadow = true;
        parentGroup.add(shoulders);
        
        const collarGeometry = new THREE.CylinderGeometry(0.18, 0.16, 0.05, 32);
        const collar = new THREE.Mesh(collarGeometry, clothingMaterial);
        collar.position.y = 1.18;
        parentGroup.add(collar);
    }
    
    setupProceduralMorphTargets() {
        this.proceduralVisemeShapes = {
            0: {
                upperLipScale: { x: 1.2, y: 0.6, z: 0.8 },
                lowerLipScale: { x: 1.1, y: 0.8, z: 0.8 },
                upperLipPos: { y: 0.02 },
                lowerLipPos: { y: -0.02 },
                showTeeth: false,
                showTongue: false
            },
            1: {
                upperLipScale: { x: 0.8, y: 0.6, z: 1.2 },
                lowerLipScale: { x: 0.7, y: 0.6, z: 1.2 },
                upperLipPos: { y: 0.01 },
                lowerLipPos: { y: -0.01 },
                showTeeth: false,
                showTongue: false
            },
            5: {
                upperLipScale: { x: 1.0, y: 0.3, z: 0.6 },
                lowerLipScale: { x: 1.0, y: 0.3, z: 0.6 },
                upperLipPos: { y: -0.01 },
                lowerLipPos: { y: 0.01 },
                showTeeth: false,
                showTongue: false
            },
            6: {
                upperLipScale: { x: 1.0, y: 0.4, z: 0.8 },
                lowerLipScale: { x: 1.0, y: 0.8, z: 0.8 },
                upperLipPos: { y: 0 },
                lowerLipPos: { y: -0.03 },
                showTeeth: true,
                showTongue: false
            },
            7: {
                upperLipScale: { x: 1.1, y: 0.5, z: 0.8 },
                lowerLipScale: { x: 1.0, y: 0.5, z: 0.8 },
                upperLipPos: { y: 0.01 },
                lowerLipPos: { y: -0.01 },
                showTeeth: true,
                showTongue: true
            },
            9: {
                upperLipScale: { x: 1.1, y: 0.4, z: 0.8 },
                lowerLipScale: { x: 1.0, y: 0.4, z: 0.8 },
                upperLipPos: { y: 0.005 },
                lowerLipPos: { y: -0.005 },
                showTeeth: true,
                showTongue: false
            },
            13: {
                upperLipScale: { x: 1.0, y: 0.4, z: 0.8 },
                lowerLipScale: { x: 1.0, y: 0.4, z: 0.8 },
                upperLipPos: { y: 0 },
                lowerLipPos: { y: 0 },
                showTeeth: false,
                showTongue: false
            }
        };
        
        this.currentMouthState = {
            upperLipScale: { x: 1.0, y: 0.4, z: 0.8 },
            lowerLipScale: { x: 1.0, y: 0.4, z: 0.8 },
            upperLipPos: { y: 0 },
            lowerLipPos: { y: 0 },
            showTeeth: false,
            showTongue: false
        };
    }
    
    setupFacialExpressionSystem() {
        console.log('Setting up facial expression system');
        
        Object.keys(this.expressions).forEach(expr => {
            if (expr !== 'neutral') {
                this.expressions[expr].intensity = 0;
                this.expressions[expr].target = 0;
            }
        });
    }
    
    setupIdleAnimations() {
        this.idleSystem.lastBlinkTime = Date.now();
        this.idleSystem.nextBlinkTime = Date.now() + this.idleSystem.blinkInterval + Math.random() * 2000;
    }
    
    setExpression(expression, intensity = 1.0, duration = 500) {
        if (!this.expressions[expression]) {
            console.warn(`Unknown expression: ${expression}`);
            return;
        }
        
        this.expressions[expression].target = Math.max(0, Math.min(1, intensity));
        
        const emotions = ['happy', 'sad', 'angry', 'surprised', 'disgusted', 'fearful'];
        if (emotions.includes(expression) && intensity > 0) {
            emotions.forEach(emotion => {
                if (emotion !== expression) {
                    this.expressions[emotion].target = 0;
                }
            });
            this.expressions.neutral.target = 0;
        }
        
        console.log(`Setting expression ${expression} to ${intensity}`);
    }
    
    triggerExpression(expression, intensity = 1.0, duration = 2000) {
        this.setExpression(expression, intensity);
        
        setTimeout(() => {
            this.setExpression(expression, 0);
            this.setExpression('neutral', 1);
        }, duration);
    }
    
    setEyeLookDirection(x, y) {
        const clampedX = Math.max(-1, Math.min(1, x));
        const clampedY = Math.max(-1, Math.min(1, y));
        
        this.expressions.eyeLeftLeft.target = clampedX < 0 ? -clampedX : 0;
        this.expressions.eyeLeftRight.target = clampedX > 0 ? clampedX : 0;
        this.expressions.eyeLeftUp.target = clampedY > 0 ? clampedY : 0;
        this.expressions.eyeLeftDown.target = clampedY < 0 ? -clampedY : 0;
        
        this.expressions.eyeRightLeft.target = clampedX < 0 ? -clampedX : 0;
        this.expressions.eyeRightRight.target = clampedX > 0 ? clampedX : 0;
        this.expressions.eyeRightUp.target = clampedY > 0 ? clampedY : 0;
        this.expressions.eyeRightDown.target = clampedY < 0 ? -clampedY : 0;
    }
    
    blink(eye = 'both') {
        const blinkDuration = 150;
        
        if (eye === 'both' || eye === 'left') {
            this.expressions.eyeBlinkLeft.target = 1;
            setTimeout(() => {
                this.expressions.eyeBlinkLeft.target = 0;
            }, blinkDuration);
        }
        
        if (eye === 'both' || eye === 'right') {
            this.expressions.eyeBlinkRight.target = 1;
            setTimeout(() => {
                this.expressions.eyeBlinkRight.target = 0;
            }, blinkDuration);
        }
    }
    
    setViseme(visemeIndex, weight) {
        if (visemeIndex >= 0 && visemeIndex < this.targetVisemeWeights.length) {
            this.targetVisemeWeights[visemeIndex] = Math.max(0, Math.min(1, weight));
        }
    }
    
    update(deltaTime) {
        if (!this.avatarModel) return;
        
        if (this.avatarMixer) {
            this.avatarMixer.update(deltaTime);
        }
        
        this.updateIdleAnimations(deltaTime);
        this.updateFacialExpressions(deltaTime);
        this.updateVisemeBlending(deltaTime);
        this.applyExpressionsToModel();
        
        if (this.controls) {
            this.controls.update();
        }
    }
    
    updateIdleAnimations(deltaTime) {
        if (!this.idleSystem.enabled) return;
        
        const currentTime = Date.now();
        
        if (currentTime > this.idleSystem.nextBlinkTime) {
            this.blink();
            this.idleSystem.lastBlinkTime = currentTime;
            this.idleSystem.nextBlinkTime = currentTime + 
                this.idleSystem.blinkInterval + 
                Math.random() * 3000;
        }
        
        this.idleSystem.breathingTime += deltaTime;
        const breathScale = 1 + Math.sin(this.idleSystem.breathingTime * 1.2) * this.idleSystem.breathingIntensity;
        if (this.avatarModel) {
            this.avatarModel.scale.y = breathScale;
        }
        
        this.idleSystem.headMovementTime += deltaTime;
        if (this.avatarMesh) {
            const headSway = Math.sin(this.idleSystem.headMovementTime * 0.7) * 0.01;
            const headNod = Math.sin(this.idleSystem.headMovementTime * 0.5) * 0.005;
            this.avatarMesh.rotation.z = headSway;
            this.avatarMesh.rotation.x = headNod;
        }
        
        this.idleSystem.eyeMovementTime += deltaTime;
        if (this.idleSystem.eyeMovementTime > 3) {
            const eyeX = (Math.random() - 0.5) * 0.3;
            const eyeY = (Math.random() - 0.5) * 0.2;
            this.setEyeLookDirection(eyeX, eyeY);
            this.idleSystem.eyeMovementTime = 0;
        }
        
        this.idleSystem.microExpressionTime += deltaTime;
        if (this.idleSystem.microExpressionTime > 8) {
            const microExpressions = ['happy', 'surprised', 'neutral'];
            const randomExpression = microExpressions[Math.floor(Math.random() * microExpressions.length)];
            this.triggerExpression(randomExpression, 0.1, 1000);
            this.idleSystem.microExpressionTime = 0;
        }
    }
    
    updateFacialExpressions(deltaTime) {
        Object.keys(this.expressions).forEach(exprName => {
            const expr = this.expressions[exprName];
            const diff = expr.target - expr.intensity;
            
            expr.intensity += diff * this.expressionBlendSpeed;
            
            if (exprName !== 'neutral' && expr.target === 0) {
                expr.intensity *= this.emotionDecayRate;
            }
            
            expr.intensity = Math.max(0, Math.min(1, expr.intensity));
            
            if (Math.abs(diff) < 0.001) {
                expr.intensity = expr.target;
            }
        });
    }
    
    updateVisemeBlending(deltaTime) {
        for (let i = 0; i < this.visemeWeights.length; i++) {
            const target = this.targetVisemeWeights[i];
            const current = this.visemeWeights[i];
            const diff = target - current;
            
            this.visemeWeights[i] += diff * this.visemeBlendSpeed;
            
            if (Math.abs(diff) < 0.001) {
                this.visemeWeights[i] = target;
            }
        }
    }
    
    applyExpressionsToModel() {
        if (this.avatarMesh && this.avatarMesh.morphTargetInfluences) {
            Object.keys(this.expressions).forEach(exprName => {
                const morphIndex = this.morphTargets.get(exprName);
                if (morphIndex !== undefined) {
                    this.avatarMesh.morphTargetInfluences[morphIndex] = this.expressions[exprName].intensity;
                }
            });
            
            for (let i = 0; i < this.visemeWeights.length; i++) {
                const morphIndex = this.morphTargets.get(`viseme_${i}`);
                if (morphIndex !== undefined) {
                    this.avatarMesh.morphTargetInfluences[morphIndex] = this.visemeWeights[i];
                }
            }
        } else {
            this.applyToProceduralAvatar();
        }
    }
    
    applyToProceduralAvatar() {
        if (this.leftEye && this.rightEye) {
            const leftBlinkIntensity = this.expressions.eyeBlinkLeft.intensity;
            const rightBlinkIntensity = this.expressions.eyeBlinkRight.intensity;
            
            this.leftEye.scale.y = 1 - leftBlinkIntensity * 0.8;
            this.rightEye.scale.y = 1 - rightBlinkIntensity * 0.8;
            
            const eyeMovementRange = 0.02;
            const leftEyeX = (this.expressions.eyeLeftRight.intensity - this.expressions.eyeLeftLeft.intensity) * eyeMovementRange;
            const leftEyeY = (this.expressions.eyeLeftUp.intensity - this.expressions.eyeLeftDown.intensity) * eyeMovementRange;
            const rightEyeX = (this.expressions.eyeRightRight.intensity - this.expressions.eyeRightLeft.intensity) * eyeMovementRange;
            const rightEyeY = (this.expressions.eyeRightUp.intensity - this.expressions.eyeRightDown.intensity) * eyeMovementRange;
            
            if (this.leftEyeBall) {
                this.leftEyeBall.position.x = leftEyeX;
                this.leftEyeBall.position.y = leftEyeY;
            }
            if (this.rightEyeBall) {
                this.rightEyeBall.position.x = rightEyeX;
                this.rightEyeBall.position.y = rightEyeY;
            }
        }
        
        this.applyVisemesToProceduralMouth();
        this.applyEmotionsToProceduralHead();
    }
    
    applyVisemesToProceduralMouth() {
        if (!this.upperLip || !this.lowerLip) return;
        
        let dominantViseme = 13;
        let maxWeight = 0;
        
        for (let i = 0; i < this.visemeWeights.length; i++) {
            if (this.visemeWeights[i] > maxWeight) {
                maxWeight = this.visemeWeights[i];
                dominantViseme = i;
            }
        }
        
        const targetShape = this.proceduralVisemeShapes[dominantViseme] || this.proceduralVisemeShapes[13];
        
        const blendFactor = 0.1;
        
        this.currentMouthState.upperLipScale.x += (targetShape.upperLipScale.x - this.currentMouthState.upperLipScale.x) * blendFactor;
        this.currentMouthState.upperLipScale.y += (targetShape.upperLipScale.y - this.currentMouthState.upperLipScale.y) * blendFactor;
        this.currentMouthState.upperLipScale.z += (targetShape.upperLipScale.z - this.currentMouthState.upperLipScale.z) * blendFactor;
        
        this.currentMouthState.lowerLipScale.x += (targetShape.lowerLipScale.x - this.currentMouthState.lowerLipScale.x) * blendFactor;
        this.currentMouthState.lowerLipScale.y += (targetShape.lowerLipScale.y - this.currentMouthState.lowerLipScale.y) * blendFactor;
        this.currentMouthState.lowerLipScale.z += (targetShape.lowerLipScale.z - this.currentMouthState.lowerLipScale.z) * blendFactor;
        
        this.upperLip.scale.set(
            this.currentMouthState.upperLipScale.x,
            this.currentMouthState.upperLipScale.y,
            this.currentMouthState.upperLipScale.z
        );
        
        this.lowerLip.scale.set(
            this.currentMouthState.lowerLipScale.x,
            this.currentMouthState.lowerLipScale.y,
            this.currentMouthState.lowerLipScale.z
        );
        
        if (targetShape.upperLipPos) {
            this.upperLip.position.y = 1.63 + (targetShape.upperLipPos.y || 0);
        }
        if (targetShape.lowerLipPos) {
            this.lowerLip.position.y = 1.57 + (targetShape.lowerLipPos.y || 0);
        }
        
        if (this.teeth) {
            this.teeth.visible = targetShape.showTeeth && maxWeight > 0.3;
        }
        if (this.tongue) {
            this.tongue.visible = targetShape.showTongue && maxWeight > 0.5;
        }
    }
    
    applyEmotionsToProceduralHead() {
        if (!this.avatarMesh) return;
        
        const happyIntensity = this.expressions.happy.intensity;
        const sadIntensity = this.expressions.sad.intensity;
        const angryIntensity = this.expressions.angry.intensity;
        
        const headTiltX = (happyIntensity * 0.05) - (sadIntensity * 0.1) + (angryIntensity * 0.03);
        const headTiltZ = (happyIntensity * 0.02) - (angryIntensity * 0.02);
        
        this.avatarMesh.rotation.x += headTiltX * 0.1;
        this.avatarMesh.rotation.z += headTiltZ * 0.1;
    }
    
    startAnimation() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        this.animate();
    }
    
    stopAnimation() {
        this.isAnimating = false;
    }
    
    animate() {
        if (!this.isAnimating) return;
        
        const deltaTime = this.clock.getDelta();
        
        this.update(deltaTime);
        this.renderer.render(this.scene, this.camera);
        
        requestAnimationFrame(this.animate);
    }
    
    onProgress(progress) {
        if (progress.lengthComputable) {
            const percentComplete = (progress.loaded / progress.total) * 100;
            console.log(`Model loading: ${percentComplete.toFixed(1)}%`);
        }
    }
    
    onError(error, reject) {
        console.error('Failed to load avatar model:', error);
        reject(error);
    }
    
    onWindowResize() {
        if (!this.camera || !this.renderer || !this.canvas) return;
        
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    setIdleAnimationsEnabled(enabled) {
        this.idleSystem.enabled = enabled;
        if (!enabled) {
            this.setExpression('neutral', 1);
            this.setEyeLookDirection(0, 0);
        }
    }
    
    setAnimationParameters(params) {
        if (params.expressionBlendSpeed !== undefined) {
            this.expressionBlendSpeed = Math.max(0.01, Math.min(1, params.expressionBlendSpeed));
        }
        
        if (params.visemeBlendSpeed !== undefined) {
            this.visemeBlendSpeed = Math.max(0.01, Math.min(1, params.visemeBlendSpeed));
        }
        
        if (params.emotionDecayRate !== undefined) {
            this.emotionDecayRate = Math.max(0.8, Math.min(1, params.emotionDecayRate));
        }
        
        if (params.blinkInterval !== undefined) {
            this.idleSystem.blinkInterval = Math.max(1000, params.blinkInterval);
        }
    }
    
    getExpressionStates() {
        const states = {};
        Object.keys(this.expressions).forEach(expr => {
            states[expr] = this.expressions[expr].intensity;
        });
        return states;
    }
    
    resetExpressions() {
        Object.keys(this.expressions).forEach(expr => {
            if (expr !== 'neutral') {
                this.expressions[expr].target = 0;
                this.expressions[expr].intensity = 0;
            }
        });
        this.expressions.neutral.target = 1;
        this.expressions.neutral.intensity = 1;
    }
    
    resetVisemes() {
        this.targetVisemeWeights.fill(0);
        this.targetVisemeWeights[13] = 1;
        this.visemeWeights.fill(0);
        this.visemeWeights[13] = 1;
    }
    
    cleanup() {
        this.stopAnimation();
        
        if (this.avatarMixer) {
            this.avatarMixer.uncacheRoot(this.avatarModel);
        }
        
        if (this.avatarModel) {
            this.avatarModel.traverse((child) => {
                if (child.geometry) {
                    child.geometry.dispose();
                }
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(material => material.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            });
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        window.removeEventListener('resize', this.onWindowResize);
        
        console.log('Avatar Controller cleaned up');
    }
}