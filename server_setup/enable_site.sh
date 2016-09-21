#!/usr/bin/env bash

DOMAIN_NAME=${1}

a2ensite ${DOMAIN_NAME}
service apache2 reload
