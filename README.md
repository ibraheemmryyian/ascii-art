# ASCII Art Widgets & Apps

A collection of high-performance, real-time ASCII art visualizers for Windows, featuring live audio spectrum tracking and AI-enhanced camera face tracking.

## 🚀 Features

### 🎵 Audio Spectrum Widget (`visualizer.py`)
A sleek, minimal desktop widget that reacts to your system's audio output.
*   **WASAPI Loopback**: Accurately tracks system audio (Spotify, YouTube, etc.) instead of just the microphone.
*   **Desktop Integrated**: Pushes itself behind active windows to act as a live wallpaper element.
*   **Frosted Glass Aesthetic**: 65% transparency with a high-contrast dark slate and cyan theme.
*   **Draggable**: Click and drag anywhere to reposition.

### 📷 Camera Face Tracker Pro (`camera_app.py`)
A high-resolution, resizable application that turns your webcam feed into live ASCII art.
*   **CLAHE Enhancement**: Uses Contrast Limited Adaptive Histogram Equalization to make facial features pop.
*   **Aspect-Ratio Aware**: Automatically crops the camera feed to match your window dimensions without stretching.
*   **Dynamically Resizable**: The ASCII grid recalculates in real-time as you scale the window.
*   **High-Contrast Mode**: Sharp white-on-black rendering for maximum detail.

---

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ibraheemmryyian/ascii-art.git
    cd ascii-art
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

### To run the Audio Visualizer:
```bash
python visualizer.py
```

### To run the Camera Pro App:
```bash
python camera_app.py
```

## 🖱️ Controls
*   **Widgets**: Double-click anywhere to exit. Click and drag to move.
*   **Camera App**: Standard window controls (Maximize/Minimize/Close).

---
*Created with ❤️ for fun.*
