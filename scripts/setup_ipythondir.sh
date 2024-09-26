#!/usr/bin/env bash

# Define the path to the _environment.local file
ENV_FILE="_environment.local"

# Get the current directory (expanded path)
CURRENT_DIR=$(pwd)

# Define the IPYTHONDIR line
IPYTHONDIR="${CURRENT_DIR}/.ipython"
IPYTHONDIR_LINE="IPYTHONDIR=${IPYTHONDIR}"

# Define the URL and the destination file name
URL="https://github.com/cu-esiil-edu/esiil-learning-portal/releases/download/data-release/db.zip"
DEST="${IPYTHONDIR}/profile_default"
DEST_DIR="db"

# Download the ZIP file using wget
wget $URL -O $DEST

# Create the directory to extract to
mkdir -p $DEST_DIR

# Extract the ZIP file
unzip $DEST -d $DEST_DIR

# Clean up by removing the downloaded ZIP file
rm $DEST

echo "Download and extraction complete."

# Ensure the file ends with a newline if it exists
if [ -f "$ENV_FILE" ]; then
    # Add a newline at the end of the file if it doesn't already end with one
    if [ "$(tail -c 1 "$ENV_FILE")" != "" ]; then
        echo "" >> "$ENV_FILE"
    fi
fi

# Check if the IPYTHONDIR line already exists in the _environment.local file
if grep -q "^IPYTHONDIR=" "$ENV_FILE"; then
    # If it exists, update it with the new path
    sed -i.bak "s|^IPYTHONDIR=.*|$IPYTHONDIR_LINE|" "$ENV_FILE"
    echo "Updated IPYTHONDIR in $ENV_FILE"
else
    # If it doesn't exist, append the line
    echo "$IPYTHONDIR_LINE" >> "$ENV_FILE"
    echo "Added IPYTHONDIR to $ENV_FILE"
fi

# Output the current contents of _environment.local
echo "Current contents of $ENV_FILE:"
cat "$ENV_FILE"