#!/bin/bash
source "./conf/output.sh"

check_homebrew_install() {
    intro "Checking if homebrew installed..."
    if [ ! -e /usr/local/bin/brew ]; then
        installing "Installing brew now..."
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        success "Successfully installed homebrew."
        end_step
    else
        success "Homebrew requirement satisfied."
        end_step
    fi
}

check_homebrew_package() {
    local pkg=$1
    intro "Checking for brew package $pkg..."

    if [ ! -z "$(brew ls --versions $pkg 2>/dev/null)" ]; then
        success "Package $pkg exists."
        end_step
    else
        echo ""
        installing "Running 'brew install $1'"
        brew install $1
        echo ""
        end_step
    fi
}
