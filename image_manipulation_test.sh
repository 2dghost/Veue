#!/bin/bash

# Script to demonstrate basic image manipulation with ImageMagick

# Define variables
INPUT_DIR="screenshots"
OUTPUT_DIR="processed_images"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "ImageMagick Image Manipulation Demo"
echo "=================================="
echo

# Check if we have any screenshots to work with
if [ ! -d "$INPUT_DIR" ] || [ -z "$(ls -A $INPUT_DIR 2>/dev/null)" ]; then
    echo "No screenshots found in '$INPUT_DIR' directory."
    echo "Please run the screenshot_test.sh script first to capture some screenshots."
    exit 1
fi

# Get the first screenshot file
SCREENSHOT=$(ls "$INPUT_DIR"/*.png | head -1)
FILENAME=$(basename "$SCREENSHOT")
BASE_NAME="${FILENAME%.*}"

echo "Using image: $SCREENSHOT"
echo

# Example 1: Resize an image
RESIZED="${OUTPUT_DIR}/${BASE_NAME}_resized_${TIMESTAMP}.png"
echo "Example 1: Resize an image"
echo "Command: convert $SCREENSHOT -resize 50% $RESIZED"
convert "$SCREENSHOT" -resize 50% "$RESIZED"
echo "Resized image saved as $RESIZED"
echo

# Example 2: Add a border
BORDERED="${OUTPUT_DIR}/${BASE_NAME}_bordered_${TIMESTAMP}.png"
echo "Example 2: Add a border"
echo "Command: convert $SCREENSHOT -border 10 -bordercolor black $BORDERED"
convert "$SCREENSHOT" -border 10 -bordercolor black "$BORDERED"
echo "Bordered image saved as $BORDERED"
echo

# Example 3: Apply a blur effect
BLURRED="${OUTPUT_DIR}/${BASE_NAME}_blurred_${TIMESTAMP}.png"
echo "Example 3: Apply a blur effect"
echo "Command: convert $SCREENSHOT -blur 0x8 $BLURRED"
convert "$SCREENSHOT" -blur 0x8 "$BLURRED"
echo "Blurred image saved as $BLURRED"
echo

# Example 4: Convert to grayscale
GRAYSCALE="${OUTPUT_DIR}/${BASE_NAME}_grayscale_${TIMESTAMP}.png"
echo "Example 4: Convert to grayscale"
echo "Command: convert $SCREENSHOT -type Grayscale $GRAYSCALE"
convert "$SCREENSHOT" -type Grayscale "$GRAYSCALE"
echo "Grayscale image saved as $GRAYSCALE"
echo

# Example 5: Add text annotation
ANNOTATED="${OUTPUT_DIR}/${BASE_NAME}_annotated_${TIMESTAMP}.png"
echo "Example 5: Add text annotation"
echo "Command: convert $SCREENSHOT -fill white -pointsize 24 -gravity south -annotate +0+10 'Processed with ImageMagick' $ANNOTATED"
convert "$SCREENSHOT" -fill white -pointsize 24 -gravity south -annotate +0+10 'Processed with ImageMagick' "$ANNOTATED"
echo "Annotated image saved as $ANNOTATED"
echo

echo "All processed images have been saved in the '$OUTPUT_DIR' directory."
echo "You can view them using: display $OUTPUT_DIR/*.png" 