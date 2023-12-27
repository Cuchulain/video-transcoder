#!/bin/bash

# Check the number of arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <source_directory> <destination_directory> <interval_in_seconds> [ignore_mask]"
    exit 1
fi

SOURCE_DIR=$1
DEST_DIR=$2
INTERVAL=$3
IGNORE_MASK=${4:-*.part} # Set the default ignore mask to *.part if not specified

# Enable extended globbing for pattern matching with the mask
shopt -s extglob
shopt -s globstar

# Function to process video files
process_video_files() {
    find "$SOURCE_DIR" -type f -not -name "$IGNORE_MASK" | while read -r file; do
        # Check if the file is a video using ffprobe
        if ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$file" > /dev/null; then
            # Change the path for the output directory
            local relative_path="${file#$SOURCE_DIR/}"
            local dest_file="$DEST_DIR/$relative_path"
            local dest_extension="${file##*.}"

            # Check if the output file already exists
            if [ ! -f "$dest_file" ]; then
                local temp_file=$(mktemp "/tmp/recoded_video.XXXXXX.$dest_extension") # Create a temporary file with the appropriate extension

                # Call the script for video recoding with the temporary file as output
                recode_video "$file" "$temp_file" -f

                # Move the temporary file to the target location only if recode_video exits with status code 0
                if [ $? -eq 0 ]; then
                    mkdir -p "$(dirname "$dest_file")"
                    mv "$temp_file" "$dest_file"
                else
                    echo "Error in recoding video: $file"
                    rm "$temp_file" # Remove the temporary file if recoding failed
                fi
            fi
        fi
    done
}

# Main loop
while true; do
    process_video_files
    sleep "$INTERVAL"
done
