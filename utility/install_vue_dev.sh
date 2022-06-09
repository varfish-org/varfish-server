#!/usr/bin/env bash
echo "***********************************************"
echo "Installing Node.js"
echo "***********************************************"
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
apt-get install -y nodejs

echo "***********************************************"
echo "Installing Vue CLI and Init"
echo "***********************************************"
npm install -g @vue/cli
npm install -g @vue/cli-init
