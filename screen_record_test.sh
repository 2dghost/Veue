#!/bin/bash

# Simple script to demonstrate FFmpeg screen recording

# Define variables
OUTPUT_FILE="screen_recording.mp4"
DURATION=5  # Recording duration in seconds
DISPLAY=":0.0"  # Default display
RESOLUTION="1280x720"  # Recording resolution

echo "Starting screen recording for $DURATION seconds..."
echo "Recording will be saved as $OUTPUT_FILE"

# Record the screen using FFmpeg with x11grab
ffmpeg -f x11grab -s "$RESOLUTION" -i "$DISPLAY" -t "$DURATION" -c:v libx264 -preset ultrafast -pix_fmt yuv420p "$OUTPUT_FILE"

echo "Recording completed!"
echo "The recording has been saved as $OUTPUT_FILE" 