#!/bin/bash

source "./config/io.sh"
source "./config/output.sh"


validate_docker_setup(){
    intro "Validating docker setup..."

    if [ -n "$DOCKER_MACHINE_NAME" ]; then
        >&2 echo "Found docker-machine installed."
        error "Remove DOCKER_* env vars from .bash_profile."
        exit 1
    fi

    if [ ! -d "$DOCKER_CONTAINER_DIR" ]; then
        >&2 error "Docker is not installed."
        exit 1
    fi
    success "Docker correctly installed."
    end_step
}


docker_version_gt() {
    local cmp_version="${1}.a"
    local DOCKER_VERSION = $(docker version --format '{{.Server.Version}}')

    local greater_version=$(printf "$DOCKER_VERSION\n$cmp_version\n" \
        | sort -t '.' -k 1,1 -k 2,2 -k 3,3 -g | head -n1)
    [ "${greater_version}" = "${cmp_version}" ]
}


docker_enable_fstrim() {
    local pref_file="com.docker.driver.amd64-linux/disk/trim"

    echo -n "Checking for docker fstrim support..."

    pushd "$DOCKER_CONTAINER_DIR" > /dev/null

    current_val=$(git show "HEAD:$pref_file" 2>&1 2>/dev/null) ||:
    desired_val="true"
    if [ "$current_val" == "$desired_val" ]; then
        echo_okay
    else
        echo_installing "Updating docker..."

        git reset --hard > /dev/null
        mkdir -p com.docker.driver.amd64-linux/disk
        echo "$desired_val" > "$pref_file"

        git add "$pref_file"
        git commit -sm "Enabling fstrim" > /dev/null
        echo_okay
    fi

    popd > /dev/null
}

docker_enable_online_compaction() {
    echo_intro "Enabling docker on-line compaction..."
    pushd "$DOCKER_CONTAINER_DIR" > /dev/null

    git reset --hard > /dev/null
    mkdir -p com.docker.driver.amd64-linux/disk

    echo 262144 > com.docker.driver.amd64-linux/disk/compact-after
    echo 262144 > com.docker.driver.amd64-linux/disk/keep-erased
    echo -n true > com.docker.driver.amd64-linux/disk/trim

    git add com.docker.driver.amd64-linux/disk/compact-after
    git add com.docker.driver.amd64-linux/disk/keep-erased
    git add com.docker.driver.amd64-linux/disk/trim

    git commit -sm "Enable on-line compaction" > /dev/null ||:
    echo_okay

    popd > /dev/null
}

# This isn't working currently
docker_full_sync_on_flush_optimization() {
    echo_intro "Checking for docker full-sync-on-flush optimization..."

    local pref_file="com.docker.driver.amd64-linux/disk/full-sync-on-flush"
    pushd "$DOCKER_CONTAINER_DIR" > /dev/null

    current_val=$(git show "HEAD:$pref_file" 2>&1 2>/dev/null) ||:
    desired_val="false"
    if [ -z "${current_val}" ]; then
        pref_file="com.docker.driver.amd64-linux/disk/on-flush"
        current_val=$(git show "HEAD:$pref_file" 2>&1 2>/dev/null) ||:
    fi
    if [ "$current_val" == "$desired_val" ]; then
        echo_ok
    else
        echo_installing "Updating docker..."

        git reset --hard > /dev/null
        mkdir -p com.docker.driver.amd64-linux/disk
        echo "$desired_val" > "$pref_file"

        git add "$pref_file"
        git commit -sm "Set full-sync-on-flush to false" > /dev/null
        echo_ok
    fi

    popd > /dev/null
}

docker_memory_setting_check() {
    echo_intro "Checking that docker is allocated at least 6 GB memory..."

    local pref_file="com.docker.driver.amd64-linux/memoryMiB"
    pushd "$DOCKER_CONTAINER_DIR" > /dev/null

    current_val=$(git show "HEAD:$pref_file" 2>&1 2>/dev/null) ||:
    if [ "$current_val" -ge "6144" ]; then
        echo_okay
    else
        echo_installing "Setting memory allocation to 6 GB"
        git reset --hard > /dev/null
        echo "6144" > "$pref_file"
        git add "$pref_file"
        git commit -sm "Setting memory allocation to 6 GB" > /dev/null
        echo_okay
    fi

    popd > /dev/null
}

docker_prepare(){
    docker_full_sync_on_flush_optimization
    docker_enable_fstrim

    if [ -d "$DOCKER_CONTAINER_DIR" ] && [ -d "${DOCKER_CONTAINER_DIR}/.git/refs" ]; then
        docker_full_sync_on_flush_optimization
        docker_enable_fstrim
        if docker_version_gt 17.5; then
            docker_enable_online_compaction
        fi
        docker_memory_setting_check
    fi
}
