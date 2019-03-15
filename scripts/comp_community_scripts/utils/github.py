from __future__ import print_function

import socket


__all__ = ('github_is_online', )


def github_is_online():
    s = socket.socket()
    try:
        s.connect(('github.com', 22))
    except:
        return False
    else:
        return True
