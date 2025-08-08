#!/usr/bin/env bash

echo "***********************************************"
echo "Apt-get update"
echo "***********************************************"
apt-get -y update

echo "***********************************************"
echo "Installing general OS dependencies"
echo "***********************************************"
apt-get -y install build-essential
apt-get -y install python3-dev
apt-get -y install curl

echo "***********************************************"
echo "Installing Pillow and pylibmc dependencies"
echo "***********************************************"
apt-get -y install zlib1g-dev
apt-get -y install libtiff5-dev
apt-get -y install libjpeg8-dev
apt-get -y install libfreetype6-dev
apt-get -y install liblcms2-dev
apt-get -y install libwebp-dev

echo "***********************************************"
echo "Installing Postgresql and psycopg2 dependencies"
echo "***********************************************"
apt-get -y install libpq-dev

echo "***********************************************"
echo "Installing django-extensions dependencies"
echo "***********************************************"
apt-get -y install graphviz-dev

echo "***********************************************"
echo "Installing SAML dependencies"
echo "***********************************************"
apt-get -y install xmlsec1

echo "***********************************************"
echo "Installing lxml dependencies"
echo "***********************************************"
apt-get -y install libxml2-dev
apt-get -y install libxslt-dev
