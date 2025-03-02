# Veue

**Veue** is a minimalist screen recording and screenshot application designed exclusively for Ubuntu. It offers a simple interface to record screen areas or capture screenshots, with options to save recordings as `.mp4` or `.gif` and screenshots as `.png` or `.jpeg`.

**Note**: This application is built for Ubuntu and relies on Ubuntu-specific tools (e.g., X11, FFmpeg, ImageMagick). It is not compatible with other operating systems.

## Features
- **Screen Recording**: Select an area, countdown from 2 seconds, and record with pause/resume and start-over controls.
- **Screenshots**: Capture a selected screen area with a two-click process.
- **Preview**: View recordings (with playback option) or screenshots before saving.
- **Save Options**: Recordings as `.mp4` or `.gif`, screenshots as `.png` or `.jpeg`.

## Prerequisites
- Ubuntu (tested on 20.04 and later)
- Python 3 (`python3`)
- GTK 3 for Python (`python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-3.0`)
- FFmpeg (`ffmpeg`) for recording and GIF conversion
- ImageMagick (`imagemagick`) for screenshots

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/2dghost/Veue.git
   cd Veue
   ```
2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 ffmpeg imagemagick
   ```
4. **Verify Setup**:
   - Ensure `python3 --version`, `ffmpeg -version`, and `magick -version` return valid outputs.

## Usage
1. **Run the App**:
   ```bash
   python3 main.py
   ```
   Or use the provided helper script:
   ```bash
   ./run_app.sh
   ```

2. **Recording**:
   - Click "Record," select an area, wait for the countdown.
   - Use the control bar:
     - "Pause" to pause/resume.
     - "Start Over" to reset.
     - "End" to finish and preview.
   - In the preview, click "Play" to view, or "File" → "Save As..." to save as `.mp4` or `.gif`.

3. **Screenshot**:
   - Click "Screenshot," click once to start, click again to capture.
   - Preview appears; use "File" → "Save As..." to save as `.png` or `.jpeg`.

## Keyboard Shortcuts
- **Escape**: Close the application or return to the main window
- **Space**: Pause/resume recording (when recording is active)

## Application Structure
The application consists of the following components:
- `main.py`: The main application file that creates the GUI
- `MainApplication`: A small, undecorated window with "Record" and "Screenshot" buttons
- `AreaSelector`: Allows selecting a specific area of the screen
- `CountdownWindow`: Displays a countdown before starting screen recording
- `ControlWindow`: Provides controls during recording
- `PreviewWindow`: Displays recordings and screenshots before saving

## Troubleshooting
- **No Video Playback**: Install a player like VLC (`sudo apt-get install vlc`) or Totem (`sudo apt-get install totem`).
- **GIF Errors**: Ensure FFmpeg is installed and the recording file exists.
- **Dependencies Missing**: Re-run the installation commands above.

## Development
When developing, always make sure to activate the virtual environment first:
```bash
source venv/bin/activate
```
Or use the helper script:
```bash
source venv_helper.sh activate
```

## Helper Scripts
The project includes several helper scripts:
- `venv_helper.sh`: Manage the Python virtual environment
- `run_app.sh`: Run the application with the virtual environment automatically activated

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to report bugs, suggest features, and submit code changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 