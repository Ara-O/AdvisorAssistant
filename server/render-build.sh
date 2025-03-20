#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi

# Get the major version number from Chrome
CHROME_VERSION=$(/opt/render/project/.render/chrome/opt/google/chrome/chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Detected Chrome major version: $CHROME_VERSION"

# Fetch the latest ChromeDriver release for that major version
LATEST_RELEASE=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION})
echo "Latest ChromeDriver for version ${CHROME_VERSION}: ${LATEST_RELEASE}"

# Download and install that ChromeDriver version
wget -O /tmp/chromedriver.zip "http://chromedriver.storage.googleapis.com/${LATEST_RELEASE}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /opt/render/project/bin
rm /tmp/chromedriver.zip
