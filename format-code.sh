#!/usr/bin/env bash

TARGET="${1}"
if [[ "${TARGET}" == "" ]]; then
    TARGET="."
fi

set -euxo pipefail

autoflake --recursive --in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports "${TARGET}"
pybetter --exclude=B004 "${TARGET}"
isort "${TARGET}"
blue "${TARGET}"
docformatter --recursive --in-place "${TARGET}"

echo " * * * Target '${TARGET}' processed fully.        * * *"
echo " * * * Style verification completed successfully! * * *"
echo " * * * You may now commit the changes.            * * *"
