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

  # Use the correct path for Chrome binary to get the version
  CHROME_VERSION=$(/opt/render/project/.render/chrome/opt/google/chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+')

  # Download the matching ChromeDriver
  wget -P ./ "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip"
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
  cd $HOME/project/src
else
  echo "...Using ChromeDriver from cache"
fi

# Add ChromeDriver to PATH
export PATH="${PATH}:/opt/render/project/.render/chromedriver"
