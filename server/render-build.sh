#!/usr/bin/env bash
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# --- Download and install Google Chrome ---
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src
else
  echo "...Using Chrome from cache"
fi

# --- Download and install ChromeDriver ---
if [[ ! -f $STORAGE_DIR/chrome/chromedriver ]]; then
  echo "...Downloading ChromeDriver"
  CHROMEDRIVER_VERSION=116.0.5845.96  # Replace with your actual version
  wget -P $STORAGE_DIR/chrome https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
  unzip $STORAGE_DIR/chrome/chromedriver_linux64.zip -d $STORAGE_DIR/chrome
  chmod +x $STORAGE_DIR/chrome/chromedriver
  rm $STORAGE_DIR/chrome/chromedriver_linux64.zip
else
  echo "...Using ChromeDriver from cache"
fi

# --- Update PATH ---
export PATH="${PATH}:${STORAGE_DIR}/chrome/opt/google/chrome:${STORAGE_DIR}/chrome"
