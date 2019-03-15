#!/bin/bash

declare BLACK="0;30"
declare RED="0;31"
declare GREEN="0;32"
declare ORANGE="0;33"
declare BLUE="0;34"
declare PURPLE="0;35"
declare CYAN="0;36"
declare LIGHTGRAY="0;37"
declare DARKGRAY="1;30"
declare LIGHTRED="1;31"
declare LIGHTGREEN="1;32"
declare YELLOW="1;33"
declare LIGHTBLUE="1;34"
declare LIGHTPURPLE="1;35"
declare LIGHTCYAN="1;36"
declare WHITE="1;37"
declare NC='\033[0m' # No Color

printc () {
    local color=$2
    local color_string="\033[${color}m"
    echo >&2 -e "$color_string$1$NC"
    # printf "${color_string}${1}${NC}\n"
}

success() {
    printc "$1" $GREEN
}

prompt() {
    local  __resultvar=$1
    printc "$2" $DARKGRAY
    read value
    eval $__resultvar=$value
}

intro(){
    printc "$1" $LIGHTCYAN
}

warning() {
    printc "$1" $YELLOW
}

error() {
    printc "$1" $RED
}

installing() {
    printc "$1" $BLUE
}

end_step() {
    printf "\n"
}

newline() {
    printf "\n"
}

throw_error() {
    local color=${RED}
    local color_string="\033[${color}m"

    echo >&2 -e "$color_string$1$NC"
    exit 1
}
