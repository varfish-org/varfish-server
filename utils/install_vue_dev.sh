#!/usr/bin/env bash
echo "***********************************************"
echo "Installing Node.js"
echo "***********************************************"
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
