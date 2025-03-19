#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# Install Chrome if not cached
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Return to original directory
else
  echo "...Using Chrome from cache"
fi

# Add Chrome to PATH before using it
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

# Install ChromeDriver if not cached
if [[ ! -d $STORAGE_DIR/chromedriver ]]; then
  echo "...Downloading ChromeDriver"
  mkdir -p $STORAGE_DIR/chromedriver
  cd $STORAGE_DIR/chromedriver

  # Get the full version from Chrome binary (e.g., "134.0.6998.0")
  CHROME_VERSION_FULL=$(/opt/render/project/.render/chrome/opt/google/chrome/google-chrome --version | awk '{print $3}')
  
  # Extract the major.minor.build (e.g., "134.0.6998")
  CHROME_VERSION_PREFIX=$(echo $CHROME_VERSION_FULL | cut -d'.' -f1-3)
  
  # Query the latest available ChromeDriver version for your Chrome version
  CHROME_DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION_PREFIX}")
  
  echo "Using Chrome version: $CHROME_VERSION_FULL"
  echo "Matching ChromeDriver version: $CHROME_DRIVER_VERSION"
  
  wget -P ./ "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip"
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
  cd $HOME/project/src
else
  echo "...Using ChromeDriver from cache"
fi

# Add ChromeDriver to PATH
export PATH="${PATH}:/opt/render/project/.render/chromedriver"
