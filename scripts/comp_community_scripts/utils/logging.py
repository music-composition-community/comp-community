from __future__ import print_function

import logging
from tornado.log import LogFormatter


logger = None


__all__ = ('get_logger', )


def get_logger():
    global logger

    if logger is None:
        logger = logging.getLogger('comp_community_scripts')
        logger.setLevel(logging.INFO)
        formatter = LogFormatter(
            fmt='%(color)s[%(asctime)s]%(end_color)s %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)
    return logger
