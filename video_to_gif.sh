#!/bin/bash

# Script to convert a video file to GIF using FFmpeg

# Check if input file is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_video_file> [output_gif_file]"
    echo "Example: $0 screen_recording.mp4 output.gif"
    exit 1
fi

INPUT_FILE="$1"

# Set output filename (either provided as second argument or derived from input filename)
if [ $# -ge 2 ]; then
    OUTPUT_FILE="$2"
else
    OUTPUT_FILE="${INPUT_FILE%.*}.gif"
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' does not exist."
    exit 1
fi

echo "Converting '$INPUT_FILE' to GIF..."
echo "Output will be saved as '$OUTPUT_FILE'"

# Convert video to GIF with reasonable quality
ffmpeg -i "$INPUT_FILE" -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 "$OUTPUT_FILE"

echo "Conversion completed!"
echo "GIF has been saved as '$OUTPUT_FILE'" 