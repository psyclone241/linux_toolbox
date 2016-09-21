#!/usr/bin/env bash

source config.ini

DOMAIN_NAME=${1}
SUB_DOMAIN_NAMES=${2}
OUTPUT_PATH=${3}

TEMPLATE_FILE=template_conf
FILE_EXTENSION=conf

IFS=',' read -r -a sub_domains <<< ${SUB_DOMAIN_NAMES}
IFS='. ' read -r -a is_domain_primary <<< ${DOMAIN_NAME}

function makeNewFile {
    if [ ! -z ${OUTPUT_PATH} ];
    then
        new_file_name=${OUTPUT_PATH}${1}
    else
        new_file_name=./${1}
    fi

    template_file_name=${2}
    cp ${template_file_name} ${new_file_name}
}

function replaceConfVariable {
    replace="<${1}>"
    with=${2}
    file_name=${3}

    if [ -f ${file_name} ];
    then
        echo "Replacing [${replace}] with [${with}] in ${file_name}"
        sed -i '' -e "s~${replace}~${with}~g" ${file_name}
    else
        echo "${file_name} does not exist"
    fi
}

GO=0
if [ -z "${DOMAIN_NAME}" ];
then
    echo "No domain name specified"
else
    new_file_name=${DOMAIN_NAME}.${FILE_EXTENSION}
    if [ "${#is_domain_primary[@]}" -gt 2 ];
    then
        echo "Making a subdomain"
        makeNewFile ${new_file_name} ${TEMPLATE_FILE}

        SITE_DIRECTORY=${is_domain_primary[0]}

        if [ -z "${SUB_DOMAIN_NAMES}" ];
        then
            SERVER_ALIAS="#ServerAlias"
        else
            SERVER_ALIAS="ServerAlias"
            echo "Sub Domain Names: ${SUB_DOMAIN_NAMES}"
            for sub_domain in "${!sub_domains[@]}";
            do
                sub_domain_index=${sub_domain}
                sub_domain_name=${sub_domains[sub_domain]}

                SERVER_ALIAS=${SERVER_ALIAS}" "${sub_domain_name}"."${DOMAIN_NAME}
            done
        fi

        GO=1
    else
        echo "Making Primary: ${DOMAIN_NAME}"
        makeNewFile ${new_file_name} ${TEMPLATE_FILE}

        SERVER_ALIAS="ServerAlias www.${DOMAIN_NAME}"
        if [ ! -z "${SUB_DOMAIN_NAMES}" ];
        then
            echo "Sub Domain Names: ${SUB_DOMAIN_NAMES}"
            for sub_domain in "${!sub_domains[@]}";
            do
                sub_domain_index=${sub_domain}
                sub_domain_name=${sub_domains[sub_domain]}

                SERVER_ALIAS=${SERVER_ALIAS}" "${sub_domain_name}"."${DOMAIN_NAME}
            done
        fi

        SITE_DIRECTORY=www
        GO=1
    fi

    if [ ${GO} -gt 0 ];
    then
        replaceConfVariable "SERVER_ADMIN" "${SERVER_ADMIN}" ${new_file_name}
        replaceConfVariable "SERVER_NAME" "${DOMAIN_NAME}" ${new_file_name}
        replaceConfVariable "SERVER_ALIAS" "${SERVER_ALIAS}" ${new_file_name}
        replaceConfVariable "DOCUMENT_ROOT" "${DOCUMENT_ROOT}" ${new_file_name}
        replaceConfVariable "SITE_DIRECTORY" "${SITE_DIRECTORY}" ${new_file_name}
    fi
fi

#mkdir -p /var/www/html/
