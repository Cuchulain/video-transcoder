#!/bin/bash

# Check the number of arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory> [destination_file_extension] [interval_in_seconds] [ignore_mask]"
    exit 1
fi

SOURCE_DIR=$1
DEST_DIR=$2
DEST_EXTENSION=${3:-mkv} # Set the default destination file extension to mkv if not specified
INTERVAL=${4:-30} # Set the default interval to 30s if not specified
IGNORE_MASK=${5:-*.part} # Set the default ignore mask to *.part if not specified

# Enable extended globbing for pattern matching with the mask
shopt -s extglob
shopt -s globstar

# Function to process video files
process_video_files() {
    find "$SOURCE_DIR" -type f -not -name "$IGNORE_MASK" | while read -r file; do
        # Change the path for the output directory
        local relative_path="${file#$SOURCE_DIR/}"
        local dest_file="$DEST_DIR/$relative_path"

        # Check if the output file already exists
        if [ ! -f "$dest_file" ]; then
            # Check if the file is a video using ffprobe
            if ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$file" > /dev/null; then
                # Create a temporary file with the appropriate extension
                # shellcheck disable=SC2155
                local temp_file=$(mktemp "/tmp/recoded_video.XXXXXX.$DEST_EXTENSION")

                echo "Recode $file to $temp_file"
                # Call the script for video recoding with the temporary file as output
                recode_video "$file" "$temp_file" -f

                # Move the temporary file to the target location only if recode_video exits with status code 0
                if [ $? -eq 0 ]; then
                    echo "Move $temp_file to $dest_file"
                    mkdir -p "$(dirname "$dest_file")"
                    mv "$temp_file" "$dest_file"
                else
                    echo "Error in recoding video: $file"
                    rm "$temp_file" # Remove the temporary file if recoding failed
                fi
            else
                echo "Copy $file to $dest_file"
                cp "$file" "$dest_file"
            fi
        fi
    done
}

# Main loop
while true; do
    process_video_files
    sleep "$INTERVAL"
done
