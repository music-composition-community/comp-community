#!/bin/bash

source "./config/output.sh"

pip_check_install() {
    intro "Checking for pip package '$1...'"

    if /usr/bin/env pip2 show -qqq "$1"; then
        success "Requirement ${1} already satisifed."
        end_step
    else
        installing "Installing PIP"
        /usr/bin/env pip2 install "$1"
        success "Successfully installed ${1}"
        end_step
    fi
}

check_virtualenv_install() {
    intro "Checking for virtualenv..."
    if [ -e "${PYTHON_DIR}" ]; then
        success "Found virtualenv"
        end_step
    else
        installing "Creating virtualenv"
        virtualenv --no-download --python=python3.6 "${COMP_ROOT}"
        end_step
    fi
}
