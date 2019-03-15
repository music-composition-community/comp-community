#!/usr/bin/env python
from __future__ import print_function
import os
import sys


app_ports = {
    "api": 8000,
    'admin': 3000,
}


if __name__ == '__main__':
    script_name = os.path.basename(sys.argv[0])
    if len(sys.argv) != 2:
        print("Usage: %s <app>")
        sys.exit(1)

    app_name = sys.argv[1]
    if app_name not in app_ports:
        print("Error: invalid app '%s', must be one of: %s"
            % (app_name, ", ".join(sorted(app_ports.keys()))))
        sys.exit(1)

    print("%d" % app_ports[app_name])
