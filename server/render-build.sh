#!/usr/bin/env bash
# Exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# Download and extract Chrome if not cached
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src  # Return to project root
else
  echo "...Using Chrome from cache"
fi

# Add Chrome binary to PATH
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

# Download and extract ChromeDriver if not cached
if [[ ! -d $STORAGE_DIR/chromedriver ]]; then
  echo "...Downloading ChromeDriver"
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver
  
  # Get the full Chrome version (e.g., "134.0.6998.0") using the correct binary path
  CHROME_VERSION_FULL=$(/opt/render/project/.render/chrome/opt/google/chrome/google-chrome --version | awk '{print $3}')
  
  # Extract the first three version components (e.g., "134.0.6998")
  CHROME_VERSION_PREFIX=$(echo $CHROME_VERSION_FULL | cut -d'.' -f1-3)
  
  # Query the latest matching ChromeDriver version using the version prefix
  CHROME_DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION_PREFIX}")
  
  echo "Chrome version: $CHROME_VERSION_FULL"
  echo "Matching ChromeDriver version: $CHROME_DRIVER_VERSION"
  
  # Download and unzip the matching ChromeDriver
  wget -P ./ "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip"
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
  cd $HOME/project/src
else
  echo "...Using ChromeDriver from cache"
fi

# Add ChromeDriver to PATH
export PATH="${PATH}:/opt/render/project/.render/chromedriver"
