#!/usr/bin/env bash

apt-get update
apt-get install -y ufw git virtualenv make

ufw allow https
ufw allow http
ufw allow ssh
echo y | ufw enable

adduser keyes
usermod -a -G users keyes
usermod -a -G sudo keyes

sed -i 's/PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config
service ssh restart
