#!/bin/bash

# Install dependencies (if required)
apt-get update && apt-get install -y wget unzip curl

# Find Chromium binary (Render might already have it)
CHROMIUM_PATH=$(which chromium || which chromium-browser || echo "")

if [ -z "$CHROMIUM_PATH" ]; then
    echo "Chromium is not available! Install it or use another method."
    exit 1
fi

echo "Chromium found at: $CHROMIUM_PATH"

# Get Chromium version
CHROME_VERSION=$($CHROMIUM_PATH --version | awk '{print $2}' | cut -d'.' -f1)
echo "Detected Chromium version: $CHROME_VERSION"

# Download the correct Chromedriver version
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
echo "Downloading Chromedriver version: $CHROMEDRIVER_VERSION"
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip -d $HOME/chromedriver
chmod +x $HOME/chromedriver/chromedriver

# Export paths
export CHROME_BIN="$CHROMIUM_PATH"
export PATH="$HOME/chromedriver:$PATH"

echo "Chromium and Chromedriver setup complete!"
