#!/bin/bash

# Simple script to demonstrate ImageMagick's screenshot capabilities

# Define variables
OUTPUT_DIR="screenshots"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FULL_SCREENSHOT="${OUTPUT_DIR}/full_screen_${TIMESTAMP}.png"
WINDOW_SCREENSHOT="${OUTPUT_DIR}/window_${TIMESTAMP}.png"
AREA_SCREENSHOT="${OUTPUT_DIR}/area_${TIMESTAMP}.png"

# Create screenshots directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "ImageMagick Screenshot Demo"
echo "============================"
echo

# Option 1: Capture the entire screen
echo "Option 1: Capture the entire screen"
echo "Command: import -window root $FULL_SCREENSHOT"
echo "Press Enter to capture the entire screen..."
read
import -window root "$FULL_SCREENSHOT"
echo "Full screenshot saved as $FULL_SCREENSHOT"
echo

# Option 2: Capture a specific window
echo "Option 2: Capture a specific window"
echo "Command: import -window choose $WINDOW_SCREENSHOT"
echo "Press Enter, then click on the window you want to capture..."
read
import -window choose "$WINDOW_SCREENSHOT"
echo "Window screenshot saved as $WINDOW_SCREENSHOT"
echo

# Option 3: Capture a selected area
echo "Option 3: Capture a selected area"
echo "Command: import $AREA_SCREENSHOT"
echo "Press Enter, then click and drag to select the area you want to capture..."
read
import "$AREA_SCREENSHOT"
echo "Area screenshot saved as $AREA_SCREENSHOT"
echo

echo "All screenshots have been saved in the '$OUTPUT_DIR' directory."
echo "You can view them using: display $OUTPUT_DIR/*.png" 