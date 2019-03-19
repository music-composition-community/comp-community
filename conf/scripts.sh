#!/bin/bash
set -eo pipefail
trap '{ exit 1; }' INT

source ./conf/output.sh
source ./conf/io.sh


install_comp_scripts(){
    installing "Installing comp script"
    pushd "${COMP_ROOT}/scripts" >/dev/null
    "${PYTHON_DIR}" setup.py develop
    popd > /dev/null
    end_step
}
