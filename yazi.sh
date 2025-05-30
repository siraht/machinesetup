#!/bin/bash

# Check if Snap is available
if command -v snap > /dev/null; then
    echo "Snap is available. Installing Yazi using Snap."
    sudo snap install yazi --classic
else
    echo "Snap is not available. Downloading and installing the latest binary."
    
    # Get the latest release tag from GitHub API
    LATEST_TAG=$(curl -s https://api.github.com/repos/sxyazi/yazi/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    URL="https://github.com/sxyazi/yazi/releases/download/$LATEST_TAG/yazi-x86_64-unknown-linux-gnu.zip"
    
    # Download the zip file to a temporary location
    curl -L -o /tmp/yazi.zip "$URL"
    
    # Create the yazi directory in the user's home directory
    mkdir -p ~/yazi
    
    # Extract the zip file to ~/yazi, overwriting existing files
    unzip -o /tmp/yazi.zip -d ~/yazi
    
    # Ensure the binaries are executable
    chmod +x ~/yazi/ya ~/yazi/yazi
    
    # Add aliases to .bashrc for ya and yazi binaries
    echo "alias ya='~/yazi/ya'" >> ~/.bashrc
    echo "alias yazi='~/yazi/yazi'" >> ~/.bashrc
    
    # Clean up the temporary zip file
    rm /tmp/yazi.zip
    
    # Inform the user to activate the aliases
    echo "Yazi installed. Please run 'source ~/.bashrc' or restart your terminal to use the aliases."
fi
