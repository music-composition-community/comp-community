#!/bin/bash

source "./config/output.sh"

get_sudo() {
    sudo whoami > /dev/null
}

find_port_process() {
    local port="$1"
    local pid=$(\
        sudo lsof +c 0 +M -F cLp0 -i :$port -sTCP:LISTEN \
            | head -1 \
            | perl -lne '%h=map{$&,$'"'"' if /./} split /\0/;print $h{p};')
    cmd=$(ps -o args= $pid)
    error "Process $pid is listening on port $port"
    echo "------>$cmd"
}

check_listening_ports() {
    intro "Checking for conflicting ports..."
    local ports=($(perl <<'EOF'
    @ports = grep { /^(80|443|[2345678]100)$/ }
             grep { !$seen{$_}++ }
             sort { $a <=> $b }
             map { s/^.*?\.(\d+)$/$1/g; $_; }
             map { (split /\s+/)[3] }
             grep { /LISTEN/ }
             `netstat -n -atp tcp`;
    print join(" ", @ports), "\n";
EOF
))
    if [ ! -z "$ports" ]; then
        error "Found conflicting ports..."
        newline

        local suffix=""
        if [ ${#ports[@]} -gt 1 ]; then
            suffix="es"
        fi
        >&2 error "Conflicting ports listening: ${ports[*]}"

        echo "Trying to find conflicting process${suffix} (requires sudo)..."
        get_sudo
        for port in "${ports[@]}"; do
            echo ""
            find_port_process $port
        done
        exit 1
    else
        success "Conflictings ports resolved..."
        end_step
    fi
}
