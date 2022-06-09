#!/usr/bin/env bash

echo "***********************************************"
echo "Installing LDAP/AD dependencies"
echo "***********************************************"
apt-get -y install libsasl2-dev
apt-get -y install libldap2-dev
apt-get -y install libssl-dev
