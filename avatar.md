# Project Overview

You are tasked with building a **fully local**, self-contained application (or web app) that displays a **realistic, animated female avatar** (upper torso/head) which can “speak” any user-supplied text. The user types text into a box, clicks a button, and the avatar lip-syncs while a realistic female voice is generated on the fly—**without** any cloud API calls or audio file uploads. All assets, models, and code must run on the user’s machine.

Your deliverable: A complete project structure (frontend + backend as needed) that meets these requirements. You choose the programming language(s), frameworks, and libraries—but you must explain why each choice makes sense for a fully local solution. All code should be organized into classes/modules so that future enhancements are straightforward. The final application must be comprehensible to a human reader and easy to upgrade.

---

## 2. Goals & Core Features

1. **Realistic Female Avatar (Upper Body)**

   * A 3D-rendered model showing at least head and shoulders (no full body needed).
   * Physically based (PBR) materials or high-quality textures to look lifelike.
   * Blend shapes (morph targets) or equivalent rigging so lips and jaw can animate.

2. **Text-to-Speech (TTS) Engine**

   * Locally hosted, neural (or high-quality) female voice synthesizer.
   * Input: arbitrary text string. Output: audio buffer/stream (WAV, OGG, etc.) plus phoneme/viseme timing information.
   * No audio file uploads—everything is synthesized at runtime.

3. **Real-Time Lip-Sync**

   * Map phoneme or viseme timing data from TTS to avatar blend shapes in real time.
   * Maintain a frame rate of at least 30 FPS so animation appears smooth.

4. **User Interface**

   * Single page or minimal multi-screen layout.
   * A 3D canvas area where the avatar is displayed.
   * A text box for the user to type sentences.
   * A “Speak” button (and optionally speed/pitch/volume sliders).
   * Feedback to user (e.g. “Synthesizing…” indicator, error messages if TTS fails).

5. **Local-Only Operation**

   * All models (3D avatar files, TTS model weights, any helper data) live on disk.
   * No dependency on external web services, cloud APIs, or internet connectivity at runtime.

---

## 3. High-Level Architecture Guidance

> **Note:** You decide whether to implement this as a single “all-in-one” desktop application or as a lightweight “backend + frontend” web app served locally. Each approach is acceptable, as long as nothing is hosted in the cloud.

1. **Option A: Desktop App (Electron, PyQt, etc.)**

   * Uses embedded WebView or native UI.
   * Packaging includes both TTS engine and 3D renderer (e.g., Unity, Godot, or WebGL in a window).
   * Pros: easier single-click install; bundling avoids cross-origin issues.
   * Cons: heavier bundle size; requires packaging toolchain.

2. **Option B: Local “Web App” + Local Server**

   * A minimal HTTP server runs on `localhost` and serves HTML/JS for avatar + polyfills.
   * The same server exposes a REST endpoint for TTS synthesis.
   * Front-end is implemented in the browser (any modern Chromium/Firefox).
   * Pros: keeps front-end/backend concerns separated; standard tooling (Node, Python, etc.); easy to debug.
   * Cons: user must run a local server process.

> Either option is acceptable. Whichever you choose, be explicit about how the front-end and TTS engine communicate—e.g. REST calls, local IPC, or direct function calls if everything is in one process.

---

## 4. Technical Requirements & Constraints

### 4.1. Avatar & Rendering

* **3D Format**

  * Use a standard format that supports mesh + blend shapes (morph targets) and PBR textures. Examples: **glTF 2.0**, **FBX**, or another open format.
* **Animation & Blend Shapes**

  * The avatar must include a blend-shape set for all mouth positions needed to represent speech visemes (e.g., “Ah,” “Oh,” “Ee,” etc.).
  * You must supply (or reference) a JSON mapping from phoneme names (e.g. ARPABET symbols) to blend-shape indices.
  * Avatar should also allow for a simple idle animation (e.g. slight breathing or head sway) when not speaking.
* **Rendering Engine**

  * If building a web app, use a WebGL-based library (e.g. **Three.js**, **Babylon.js**, or similar).
  * If building desktop, you may use a cross-platform engine that supports blend shapes (Unity, Godot, or a Python-based OpenGL wrapper).
  * Regardless of engine, the code that loads the avatar and sets blend-shape weights should live in a dedicated “AvatarController” class (or equivalent module) that exposes at least:

  1. `loadAvatar(modelPath, phonemeMap)` – loads the 3D model and its blend-shape dictionary.
  2. `setViseme(visemeIndex, weight)` – set the weight (0–1) of a specific viseme-blend.
  3. `update(deltaTime)` – advance any animations (idle, interpolation) per frame.

### 4.2. Text-to-Speech Engine

* **Local Neural TTS**

  * Choose an open-source TTS engine that can run offline and can output phoneme timing. Examples:

    * **Coqui TTS**, **Mozilla TTS**, **VITS**, **ESPnet TTS**, or **Festival+MaryTTS** (if phoneme timing is possible).
  * The engine must provide:

    1. A method to synthesize raw audio (WAV or similar) directly from text.
    2. A method to extract phoneme/viseme start‐and‐end timestamps (in milliseconds).
* **Phoneme → Viseme Mapping**

  * Include or reference a mapping file (e.g. `phoneme_map.json`) that maps each recognized phoneme to a numeric viseme index (which corresponds to a particular blend-shape in the avatar).
  * Example entry:

    ```json
    {
      "AH": 0,
      "AA": 0,
      "AO": 1,
      "OW": 1,
      "B": 2,
      "P": 2,
      // … etc.
    }
    ```

* **API/Interface**

  * If using a **web app + local server** architecture:

    * Expose an HTTP POST endpoint (e.g. `/synthesize`) that accepts JSON:
    * Returns JSON containing:

      * `audio_data`: base64-encoded WAV (or other browser-compatible format), or raw audio bytes if the front-end handles binary.
      * `phoneme_timings`: array of `{ "phoneme": "AH", "start_ms": 0, "end_ms": 120 }`.
  * If using a **single-process desktop app**, create a function call interface that returns the same two items: raw audio buffer + timing array.

### 4.3. Lip-Sync Logic

* **LipSyncController Class**

  * Responsibilities:

    1. Accepts phoneme/viseme timing array.
    2. On each render-frame (or a fixed interval, e.g. every 16 ms), queries the current audio playback time.
    3. Determines which viseme(s) should be active at that moment.
    4. Updates the avatar’s blend shapes (via `AvatarController.setViseme(index, weight)`).
  * Implementation details:

    * At any given time `t` (ms), find the phoneme entry where `start_ms ≤ t < end_ms`. Map that phoneme to a viseme index via the phoneme-to-viseme JSON.
    * For simplicity, you may set the corresponding blend shape to weight = 1.0 and reset all others to 0.0. (Optional: you can apply simple linear interpolation to fade in/out over ±20 ms for smoothness.)
    * When audio playback ends, reset all viseme weights to 0.

### 4.4. Audio Playback

* **AudioPlayer Class**

  * Responsibilities:

    1. Decode base64-encoded audio (if using a web app) or load raw audio from disk.
    2. Play audio with low latency and allow querying `getCurrentTimeMs()`.
    3. Provide an `onEnded` callback so that when speech finishes, the lip-sync controller can stop.
  * In a browser, use [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) to decode and play. Expose:

    ```ts
    class AudioPlayer {
      loadBase64Wav(base64: string): Promise<void>;
      play(onEndedCallback: () => void): void;
      stop(): void;
      getCurrentTimeMs(): number;
    }
    ```

  * In a desktop app, choose the appropriate audio library (e.g. PyAudio, PortAudio, SDL2) but still expose the same API surface.

---

## 5. Project Structure Suggestions

Below is a **generic** directory layout. You do **not** need to use these exact folder names, but your final deliverable should clearly separate:

* Avatar assets (3D model + textures + phoneme mapping)
* TTS engine code and model files
* Front-end code (HTML/JS/CSS) or application UI code
* Lip-sync logic modules
* Any shared utility modules (e.g. audio encoding/decoding, JSON parsing)

```
/project-root
├── assets/
│   ├── avatar_model.glb          # 3D head+shoulders with blend shapes
│   └── phoneme_map.json          # phoneme → viseme index
│
├── backend/                      # (only if you choose web app + server)
│   ├── models/                   # TTS model weights & config
│   │   └── tts_model_files/      
│   ├── tts_server.py             # code to load TTS engine & expose /synthesize
│   ├── tts_utils.py              # helper functions (e.g. align phonemes)
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # (only if you choose a web-app architecture)
│   ├── index.html                # main page with 3D canvas & controls
│   ├── css/
│   │   └── style.css             # basic layout
│   ├── js/
│   │   ├── App.js                # entry point; ties UI to controllers
│   │   ├── AvatarController.js   # loads & renders the 3D model
│   │   ├── AudioPlayer.js        # audio decode/playback
│   │   └── LipSyncController.js  # drives blend shapes based on timings
│   └── package.json              # if using npm/Node for local server
│
└── README.md                     # high-level instructions (this document)
```

If you opt for a **single-process desktop app**, you may refactor “frontend” and “backend” into a single folder, but you should still keep separate modules or classes (AvatarController, TTSController, LipSyncController, AudioPlayer).

---

## 6. Class & Module Guidelines

Every major component must live in its own class or module. Organize your code so that each responsibility is clearly encapsulated:

1. **`AvatarController` (or `AvatarModule`)**

   * Methods:

     * `loadAvatar(modelPath: string, phonemeMap: object): Promise<void>`
       • Loads 3D model, initializes blend shapes, and sets up any idle animations.
     * `setViseme(visemeIndex: number, weight: number): void`
       • Directly set one blend-shape weight (0.0–1.0).
     * `update(deltaTime: number): void`
       • Advance any time-based animations (e.g. idle breathing) and re-render scene.

2. **`TTSController` (or `TTSService`)**

   * Methods:

     * `initialize(modelsPath: string): Promise<void>`
       • Load or download TTS model weights locally.
     * `synthesize(text: string, speed: number): { audioBuffer: Uint8Array, timings: Array<{ phoneme: string, startMs: number, endMs: number }> }`
       • Produce raw audio (WAV or PCM) + phoneme timing array.
   * Must remain agnostic to how audio is played or how lip sync is driven—it only returns data.

3. **`AudioPlayer` (or `LocalAudioPlayer`)**

   * Methods:

     * `loadAudio(wavBytes: Uint8Array): Promise<void>`
       • Decode raw WAV bytes into an in-memory audio buffer.
     * `play(onEndedCallback?: Function): void`
       • Begin playback; call callback when complete.
     * `stop(): void`
       • Immediately stop playback.
     * `getCurrentTimeMs(): number`
       • Return how many milliseconds have elapsed since `play()` started.

4. **`LipSyncController`**

   * Methods:

     * `loadTimings(timings: Array<{ phoneme: string, startMs: number, endMs: number }>): void`
       • Store the phoneme timing array.
     * `start(): void`
       • Begin a loop (e.g. `requestAnimationFrame` or timer) that:

       1. Queries `AudioPlayer.getCurrentTimeMs()`
       2. Finds which timing entry covers that time
       3. Maps its phoneme → visemeIndex (via `phoneme_map.json`)
       4. Calls `AvatarController.setViseme(visemeIndex, weight)`.
     * `stop(): void`
       • End the loop and reset all blend shapes to zero.

5. **`App` (Main Orchestrator)**

   * Responsibilities:

     1. Instantiate each controller in the correct order (AvatarController, TTSController, AudioPlayer, LipSyncController).
     2. Hook up UI elements (text box, Speak button, speed slider) to drive calls to TTSController and then to AudioPlayer & LipSyncController.
     3. Handle any errors (e.g. TTS fails, missing model files) by showing an alert or on-screen message.

> All classes/modules should be well documented with comments explaining input types, output types, and expected behavior in plain English. Use meaningful names for methods and variables. Avoid overly terse or cryptic code.

---

## 7. Dependencies & Library Guidance

You are free to choose any language or framework, but keep these constraints in mind:

1. **3D Rendering**

   * **Web App**:

     * Use **Three.js** (or **Babylon.js**) for WebGL. Both support loading glTF with morph targets out of the box.
     * If bundling, use ES modules or a bundler like Webpack/Rollup/Parcel.
   * **Desktop**:

     * If you go with a C#/C++ engine (Unity, Godot), ensure it can export to a desktop binary and still allow local TTS calls.
     * If you choose Python, you could embed an OpenGL canvas via **PyQt5** or **Pygame** + **PyOpenGL**, but make sure morph targets are supported (this can be more complex).

2. **TTS Engine**

   * **Python** tends to have the richest set of offline TTS engines (Coqui TTS, Mozilla TTS, VITS).
   * If you choose another language (e.g. C++ or Rust), you must find a library that can:

     1. Run offline neural TTS—and
     2. Provide phoneme alignments.
   * **Coqui TTS** is strongly recommended because:

     * It has a simple Python API (`tts.tts_with_phonemes(...)`) that returns raw audio plus phoneme timings.
     * Pretrained English female models are publicly available.
   * If you go with a compiled language for TTS, you may need to bundle a Python interpreter or create a micro-service. Either way, ensure it remains local.

3. **Audio Decoding & Playback**

   * **Browser**: Use native Web Audio API to decode base64-encoded WAV into an `AudioBuffer` (via `decodeAudioData`) and play it.
   * **Desktop**: Use a cross-platform audio library (e.g. **PortAudio** via PyAudio, **SDL2**, or **FMOD**). Whichever you pick, it must let you query playback position in ms.

4. **JSON Parsing**

   * Every language has a standard JSON library—use it to load `phoneme_map.json` and parse TTS response (if using REST).

5. **Build Tools**

   * **Web App**: You can use a simple local server (e.g. `npm install -g live-server`) or a light Python HTTP server. Provide instructions in a README on how to launch the front-end.
   * **Desktop**: Use the language’s standard project template (e.g. `dotnet new console` for C# or `pip install pyinstaller` if you want to create a self-contained exe).

---

## 8. Code Structure & Readability Guidelines

* **Class-Based Organization**

  * Group related functionality into classes, one class per file/module.
  * Keep each class focused: AvatarController only cares about 3D loading/rendering; TTSController only cares about speech generation.

* **Naming Conventions**

  * Use descriptive names:

    * `loadAvatar()`, not `lA()`.
    * `synthesizeText()`, not `synth()`.
  * Method names should clearly indicate inputs/outputs in comments or docstrings.

* **Documentation & Comments**

  * At the top of each class, include a brief comment describing its purpose.
  * For each public method, add a comment listing:

    1. Inputs (parameters, types)
    2. Outputs (return type, structure)
    3. Side effects (e.g. “modifies internal state,” “renders a frame,” etc.).

* **Error Handling**

  * Detect and report missing assets: if the avatar model file isn’t found, throw/raise a clear error.
  * If TTS fails or model weights are missing, show a user-friendly message (e.g. “TTS engine not found—please reinstall files”).

* **File & Folder Naming**

  * Use lowercase-with-underscores or kebab-case for filenames (e.g. `avatar_controller.js`, `tts_controller.py`).
  * Put JSON assets (model configurations, phoneme maps) in an `assets/` folder.
  * Keep any third-party libraries (e.g. Three.js, TTS binaries) in a `libs/` or `vendor/` folder and document their origins in a comment.

---

## 10. Evaluation Criteria & Quality Standards

When verifying the finished project, ensure:

1. **Local-Only Functionality**

   * No network calls to external servers during TTS or avatar rendering.
   * All assets and models are stored in the project’s folder structure.

2. **Avatar Realism & Smoothness**

   * The mesh and textures look lifelike (not cartoonish).
   * Lip movement corresponds convincingly to the synthesized audio.

3. **TTS Quality**

   * The voice sounds natural, with correct pronunciation.
   * Phoneme timing is accurate (no large misalignments).

4. **Performance**

   * Lip-sync animation runs at ≥ 30 FPS on a mid-range machine.
   * Audio latency (time between clicking “Speak” and hearing sound) is under 500 ms.

5. **Code Readability & Modularity**

   * Each class/module has a single responsibility.
   * Code is sufficiently commented.
   * It is straightforward for another developer to replace or upgrade one component (e.g. swap TTS engine) without rewriting everything.

6. **Robustness / Error Handling**

   * If the user types gibberish or extremely long text, the app should not crash—either handle it gracefully or show a warning (“Text too long”).
   * If the TTS model folder is missing, display a clear error and instructions to download or reinstall.

7. **Extendability**

   * The class structure and file organization should make it obvious how to:

     * Add another voice (e.g. male).
     * Swap out the avatar for a different 3D model.
     * Introduce new controls (e.g. “Emotion: Happy/Sad”).

---

## 11. Summary

Provide these instructions to Claude Web. Claude’s job is to:

1. **Select an appropriate language** (e.g. Python + Three.js, or C#/Unity) based on these requirements.
2. **Describe and implement** each class/module as specified, using open-source libraries for TTS, 3D rendering, and audio playback.
3. **Ensure everything stays local**, leveraging local model files, local audio synthesis, and local rendering—no external calls.
4. **Structure code in classes** that are clear, maintainable, and ready for future upgrades.

Use the above sections as a blueprint. By adhering to these guidelines, Claude Web will produce a project that meets all functional, performance, and organizational requirements for a realistic, fully local talking-avatar application.
