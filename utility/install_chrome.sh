#!/usr/bin/env bash

echo "***********************************************"
echo "Installing Chrome + Driver for UI Testing"
echo "***********************************************"

# Version
CHROME_DRIVER_VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# Install dependencies
sudo apt-get update
sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

# Install Chrome
wget -N https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P ~/
sudo dpkg -i --force-depends ~/google-chrome-stable_current_amd64.deb
sudo apt-get -f install -y
rm ~/google-chrome-stable_current_amd64.deb

# Install ChromeDriver
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip
sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver
