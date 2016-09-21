#!/usr/bin/env bash

source config.ini

SITE_NAME=${1}
SUB_SITE_NAME=${2}
CREATE_INDEX=${3}

SITE_PATH=${SITE_NAME}/${SUB_SITE_NAME}

mkdir -p ${DOCUMENT_ROOT}/${SITE_PATH}
mkdir -p ${HOST_LOG_ROOT}/${SITE_PATH}

chown -R ${SITE_OWNER} ${DOCUMENT_ROOT}/${SITE_PATH}
chmod 775 ${DOCUMENT_ROOT}/${SITE_PATH}
chmod g+s ${DOCUMENT_ROOT}/${SITE_PATH}

if [ ! -z ${CREATE_INDEX} ];
then
    echo "Hello ${CREATE_INDEX}" > ${DOCUMENT_ROOT}/${SITE_PATH}/index.html
fi
