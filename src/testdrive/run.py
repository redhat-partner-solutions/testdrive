### SPDX-License-Identifier: GPL-2.0-or-later

"""Run tests"""

import json
from argparse import ArgumentParser
import sys
import os
import subprocess
from datetime import (datetime, timezone)

from .common import (open_input, print_line)
from .source import (Source, sequence)
from .uri import UriBuilder

def drive(test, *test_args):
    """Execute `test` and return a result dict.

    If `test` exits with error or outputs to stderr, then the result dict
    will contain string 'error' at key 'result' and a string at key 'reason'.

    Otherwise the result dict contains whatever `test` outputs to stdout. This
    output is always expected to be a JSON object with pairs for 'result',
    'reason' and other pairs appropriate for `test`.

    The result dict always contains `test_args` at key 'argv'.
    """
    subp = subprocess.run(
        (test,) + test_args,
        capture_output=True,
        check=False,
        env=os.environ,
    )
    if not subp.returncode and not subp.stderr:
        dct = json.loads(subp.stdout)
    else:
        reason = f'{test} exited with code {subp.returncode}'
        if subp.stderr:
            reason += '\n\n'
            reason += subp.stderr.decode()
            dct = {'result': 'error', 'reason': reason}
    dct['argv'] = test_args
    return dct

def timenow():
    """Return a datetime value for UTC time now."""
    return datetime.now(timezone.utc)

def timestamp(dtv):
    """Return an ISO 8601 string for datetime value `dtv`."""
    return datetime.isoformat(dtv)

def timevalue(string):
    """Return a datetime value for ISO 8601 `string`."""
    return datetime.fromisoformat(string)

def main():
    """Run tests"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '--basedir',
        help=' '.join((
            "The base directory which tests are relative to.",
            "If not supplied tests are relative to directory of `input`.",
        )),
    )
    aparser.add_argument(
        '--timeless', action='store_true',
        help="Do not record timestamps and times for tests.",
    )
    aparser.add_argument(
        'baseurl',
        help="The base URL which test ids are relative to.",
    )
    aparser.add_argument(
        'input',
        help=' '.join((
            "File containing tests to run or '-' to read from stdin.",
            "Each test is specified on a separate line as a JSON array.",
            "The first element is the name of the test implementation,",
            "relative to `--basedir`.",
            "The remaining elements are args to the test implementation.",
        )),
    )
    args = aparser.parse_args()
    basedir = args.basedir or os.path.dirname(args.input)
    builder = UriBuilder(args.baseurl)
    with open_input(args.input) as fid:
        source = Source(sequence(json.loads(line) for line in fid))
        for test, *test_args in source.next():
            if not args.timeless:
                start = timenow()
            result = drive(os.path.join(basedir, test), *test_args)
            if not args.timeless:
                end = timenow()
            result['id'] = builder.build(os.path.dirname(test))
            if not args.timeless:
                result['timestamp'] = timestamp(start)
                result['time'] = (end - start).total_seconds()
            # Python exits with error code 1 on EPIPE
            if not print_line(json.dumps(result)):
                sys.exit(1)

if __name__ == '__main__':
    main()
