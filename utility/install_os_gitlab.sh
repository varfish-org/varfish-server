#!/usr/bin/env bash
# Install OS dependencies for Docker image python:3.4 used in Gitlab CI
# TODO: Some of these are up-to-date on image, remove or keep just in case?

echo "***********************************************"
echo "Apt-get update"
echo "***********************************************"
apt-get -y update

echo "***********************************************"
echo "Installing OS dependencies"
echo "***********************************************"
apt-get -y install build-essential
apt-get -y install python3-dev python3-setuptools
apt-get -y install git
apt-get -y install supervisor

echo "***********************************************"
echo "Installing translation requirements"
echo "***********************************************"
apt-get -y install gettext

echo "***********************************************"
echo "Installing shared Pillow/pylibmc dependencies"
echo "***********************************************"
apt-get -y install zlib1g-dev

echo "***********************************************"
echo "Installing Posgresql and psycopg2 dependencies"
echo "***********************************************"
apt-get -y install libpq-dev

echo "***********************************************"
echo "Installing Pillow dependencies"
echo "***********************************************"
apt-get -y install libtiff5-dev
apt-get -y install libjpeg62-turbo-dev
apt-get -y install libfreetype6-dev
apt-get -y install liblcms2-dev
apt-get -y install libwebp-dev

echo "***********************************************"
echo "Installing django-extensions dependencies"
echo "***********************************************"
apt-get -y install graphviz-dev


echo "***********************************************"
echo "Installing LDAP/AD dependencies"
echo "***********************************************"
apt-get -y install libsasl2-dev
apt-get -y install libldap2-dev
