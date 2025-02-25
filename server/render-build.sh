#!/bin/bash

# Install Google Chrome (without sudo)
export CHROME_BIN="/opt/google/chrome/chrome"
curl -fsSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb
dpkg-deb -x chrome.deb $HOME/chrome
export PATH="$HOME/chrome/opt/google/chrome:$PATH"

# Install Chromedriver
CHROME_VERSION=$($CHROME_BIN --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_URL=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_URL}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip -d $HOME/chromedriver
export PATH="$HOME/chromedriver:$PATH"

# Make Chromedriver executable
chmod +x $HOME/chromedriver/chromedriver
