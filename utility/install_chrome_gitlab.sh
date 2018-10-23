#!/usr/bin/env bash

echo "***********************************************"
echo "Installing Chrome + Driver for UI Testing"
echo "***********************************************"

# Version
CHROME_DRIVER_VERSION=2.36

# Install dependencies
apt-get -y install default-jre unzip
apt-get -y install libxpm4 libxrender1 libgtk2.0-0 libnss3 libgconf-2-4
apt-get -y install xvfb gtk2-engines-pixbuf

# Install Chrome Driver
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
mv -f ~/chromedriver /usr/bin/chromedriver
chmod ugo+rx /usr/bin/chromedriver

# Install Google Chrome
set -xe
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list
apt-get update -yqqq
apt-get install -y google-chrome-stable

# wget -N https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P ~/
# dpkg -i --force-depends ~/google-chrome-stable_current_amd64.deb
