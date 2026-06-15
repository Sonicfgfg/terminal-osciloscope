# Terminal Audio Oscilloscope 📊🎵

Visualize your audio stream directly inside the terminal.

A smooth, high-performance oscilloscope written in Python that uses Unicode Braille characters for high-resolution graphics and supports both waveform rendering and XY Lissajous figures.

---

## ✨ Features

### 🎛 3 Display Modes

#### XY MODE

Classic analog oscilloscope visualization using stereo channels as X and Y axes.

#### SINGLE CHANNEL WAVE

Combined mono waveform display.

#### DUAL CHANNEL WAVE

Separate left and right channel waveform display.

---

### 🎨 Smart Line Rendering

* Thin and precise traces in XY mode for maximum detail.
* Thick and bold traces in waveform modes for improved readability.
* High-resolution rendering using Unicode Braille characters.

---

### ⚡ High Performance

* Fast Bresenham line drawing.
* NumPy vectorized rendering.
* Stable 50 FPS output.
* Low CPU usage.

---

### 🌊 Smooth Motion

Configurable smoothing factor provides a natural analog oscilloscope feel.

---

### 🐧 Compatibility

Works in most modern Linux terminals:

* Kitty
* Alacritty
* WezTerm
* Foot
* GNOME Terminal
* Konsole

---

## 🚀 Installation

### Step 1: Install System Dependencies

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install python3-dev portaudio19-dev build-essential
```

#### Fedora

```bash
sudo dnf install python3-devel portaudio-devel gcc
```

#### Arch Linux

```bash
sudo pacman -S python portaudio base-devel
```

---

### Step 2: Clone Repository

```bash
git clone https://github.com/USERNAME/terminal-scope.git
cd terminal-scope
```

---

### Step 3: Install Python Dependencies

```bash
pip install numpy pyaudio
```

---

## 🛠 Usage

```bash
python cava_scope_line.py
```

---

## 📦 Dependencies

* Python 3.9+
* NumPy
* PyAudio
* PortAudio

---

## 🔧 Technical Details

### Rendering

* Unicode Braille graphics (2×4 pixels per cell)
* Bresenham line rasterization
* NumPy bitmask rendering
* Double-buffered terminal output

### Audio Processing

* Real-time audio capture
* Stereo support
* Mono mixing mode
* Adjustable smoothing

---

## 📈 Why Braille?

Unicode Braille characters allow each terminal cell to represent a grid of:

```text
2 × 4 pixels
```

This provides significantly higher visual resolution compared to traditional ASCII graphics.

---

## ❤️ Inspired By

* Classic CRT oscilloscopes
* CAVA
* Analog audio visualization
* Retro terminal graphics

---

## 📄 License

MIT License
