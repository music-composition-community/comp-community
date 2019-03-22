#!/bin/bash
set -eo pipefail
trap '{ exit 1; }' INT

source ./config/output.sh
source ./config/io.sh


install_comp_scripts(){
    installing "Installing comp script"
    echo ${COMP_ROOT}
    pushd "${COMP_ROOT}/scripts" >/dev/null
    "${PYTHON_DIR}" setup.py develop
    popd > /dev/null
    end_step
}
