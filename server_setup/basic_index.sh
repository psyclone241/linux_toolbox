#!/usr/bin/env bash

source config.ini

SITE_NAME=${1}
SUB_SITE_NAME=${2}

SITE_PATH=${SITE_NAME}/${SUB_SITE_NAME}
INDEX_TEXT=${3}

if [ ! -z "${INDEX_TEXT}" ];
then
    echo -e "Hello ${INDEX_TEXT}" > ${DOCUMENT_ROOT}/${SITE_PATH}/index.html
fi
