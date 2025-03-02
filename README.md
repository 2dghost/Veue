# Veue Project

A screen recording and screenshot utility built with Python, GTK, FFmpeg, and ImageMagick.

## Setup Instructions

### Prerequisites

The following tools need to be installed on your system:

- Python 3.12+
- GTK for Python (PyGObject)
- FFmpeg
- ImageMagick

### Virtual Environment

This project uses a Python virtual environment to manage dependencies. Here's how to set it up:

1. **Create the virtual environment** (already done):
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```
   
   Or use the helper script:
   ```bash
   source venv_helper.sh activate
   ```

3. **Deactivate when done**:
   ```bash
   deactivate
   ```
   
   Or use the helper script:
   ```bash
   source venv_helper.sh deactivate
   ```

### Helper Scripts

The project includes several helper scripts:

- `venv_helper.sh`: Manage the Python virtual environment
  - `source venv_helper.sh activate`: Activate the virtual environment
  - `source venv_helper.sh deactivate`: Deactivate the virtual environment
  - `source venv_helper.sh status`: Check if the virtual environment is active
- `screenshot_test.sh`: Test ImageMagick screenshot capabilities
- `image_manipulation_test.sh`: Test ImageMagick image manipulation
- `screen_record_test.sh`: Test FFmpeg screen recording
- `video_to_gif.sh`: Convert videos to GIFs using FFmpeg
- `run_app.sh`: Run the application with the virtual environment automatically activated

## Application Structure

The application consists of the following components:

- `main.py`: The main application file that creates the GUI
  - `MainApplication`: A small, undecorated window with "Record" and "Screenshot" buttons
  - `AreaSelector`: Allows selecting a specific area of the screen for recording or screenshots
  - `CountdownWindow`: Displays a countdown before starting screen recording
  - `ControlWindow`: Provides controls to stop recording

## Running the Application

To run the application, make sure you have activated the virtual environment:

```bash
source venv_helper.sh activate
```

Then run the main Python file:

```bash
python main.py
```

Alternatively, you can use the provided run script which automatically handles virtual environment activation:

```bash
./run_app.sh
```

### Controls

- **Record Button**: Opens the area selector for screen recording
- **Screenshot Button**: Opens the area selector for taking screenshots
- **X Button**: Closes the application
- **Escape Key**: Closes the application or returns to the main window

### Features

- **Area Selection**: Click and drag to select a portion of the screen for recording or screenshots
- **Countdown Timer**: A 5-second countdown appears before recording begins
- **Recording Controls**: 
  - **End**: Stop recording and save the video
  - **Pause/Resume**: Temporarily pause recording and continue later
  - **Start Over**: Discard the current recording and start again
- **Recording Timer**: Shows the elapsed recording time
- **Keyboard Shortcuts**:
  - **Escape**: End recording or exit the application
  - **Space**: Pause/resume recording
- **Automatic File Naming**: 
  - Screenshots are saved with timestamps in the `screenshots` directory
  - Recordings are saved with timestamps in the `videos` directory
- **Dimension Display**: Shows the dimensions of the selected area in real-time
- **Multi-segment Recording**: Supports pausing and resuming, combining all segments into a single video file

## Development Roadmap

- **Phase 1**: Set up the development environment (completed)
- **Phase 2**: Create the main application window (completed)
- **Phase 3**: Implement area selection functionality (completed)
- **Phase 4**: Implement screen recording and screenshot capabilities (completed)
- **Phase 5**: Implement enhanced recording controls (current phase)
- **Phase 6**: Add preview functionality for recordings and screenshots

## Development

When developing, always make sure to activate the virtual environment first. This ensures that any packages you install are isolated to this project.

```bash
source venv_helper.sh activate
```

## License

[Your license information here] 