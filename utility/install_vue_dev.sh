#!/usr/bin/env bash
echo "***********************************************"
echo "Installing Node.js"
echo "***********************************************"
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "***********************************************"
echo "Installing Vue CLI and Init"
echo "***********************************************"
sudo npm install -g @vue/cli
sudo npm install -g @vue/cli-init
