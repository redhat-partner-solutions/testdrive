### SPDX-License-Identifier: GPL-2.0-or-later

"""Common code for command line tools"""

import sys
from contextlib import nullcontext

def open_input(filename, encoding='utf-8', **kwargs):
    """Return a context manager for reading from `filename`.

    If `filename` is '-' then read from stdin instead of `filename`.
    """
    if filename == '-':
        return nullcontext(sys.stdin)
    return open(filename, encoding=encoding, **kwargs)
