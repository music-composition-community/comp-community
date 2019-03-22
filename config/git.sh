#!/bin/bash

source "./config/output.sh"


set_git_config() {
    installing "Setting up basic git configuration..."
    newline

    prompt username "Enter github username: "
    prompt email "Enter github email: "

    /usr/local/bin/git config --global user.name "$username"
    /usr/local/bin/git config --global user.email "$email"

    success "Git config credentials set."
}


check_gitconfig_exists() {
    intro "Checking for ~/.gitconfig..."
    if [ -f "$HOME/.gitconfig" ]; then
        success "~/.gitconfig exists"
        end_step
    else
        set_git_config
        end_step
    fi
}
