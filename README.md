# Veue

**Veue** is a minimalist screen recording and screenshot tool built for Ubuntu. Capture your screen or take a screenshot with a lightweight, no-frills interface.

## Why Veue?
- **Screen Recording**: Record any area with a 2-second countdown, pause/resume, and restart options.
- **Screenshots**: Capture precise areas with a two-click process.
- **Preview & Save**: Review your work and save recordings as `.mp4` or `.gif`, screenshots as `.png` or `.jpeg`.
- **Ubuntu Only**: Designed for Ubuntu using native tools (X11, FFmpeg, ImageMagick, GTK).

> **Note**: This app works exclusively on Ubuntu. Other operating systems are not supported.

## Get Started

### Installation
1. **Download**: Get the latest release from the [Releases](https://github.com/2dghost/Veue/releases) tab (e.g., `Veue-v1.0.0.zip`).
2. **Extract**: Unzip the file:
   ```bash
   unzip Veue-v1.0.0.zip -d Veue
   cd Veue
   ```
3. **Set Up**: Install dependencies and run in a virtual environment:
   ```bash
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg imagemagick
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Launch**: Start the app:
   ```bash
   python3 main.py
   ```

### Usage
- **Record**: Click "Record," select an area, and use the control bar (Pause, Start Over, End). Preview and save as `.mp4` or `.gif`.
- **Screenshot**: Click "Screenshot," click twice to capture, then save as `.png` or `.jpeg` from the preview.

## License
Released under the [MIT License](https://github.com/2dghost/Veue/blob/master/LICENSE).

## Contribute
Want to help? See the [Contribution Guidelines](https://github.com/2dghost/Veue/blob/master/CONTRIBUTING.md) on the `master` branch.

## Download
Get it from [Releases](https://github.com/2dghost/Veue/releases).

---
*Veue - Simple. Fast. Ubuntu.* 