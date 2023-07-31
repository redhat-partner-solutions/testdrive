### SPDX-License-Identifier: GPL-2.0-or-later

"""Run tests"""

import json
from argparse import ArgumentParser
import os.path
import subprocess
from datetime import (datetime, timezone)

from .source import (Source, sequence)
from .uri import UriBuilder

def drive(test):
    """Execute `test` and return a result dict"""
    subp = subprocess.run(test, capture_output=True, check=False)
    if not subp.returncode and not subp.stderr:
        return json.loads(subp.stdout)
    reason = f'{test} exited with code {subp.returncode}'
    if subp.stderr:
        reason += '\n\n'
        reason += subp.stderr.decode()
    return {'result': 'error', 'reason': reason}

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
            "If not supplied tests are relative to the directory of filename.",
        )),
    )
    aparser.add_argument(
        '--timeless', action='store_true',
        help="Do not record timestamps and times for tests.",
    )
    aparser.add_argument(
        'baseurl',
        help="The base URL which tests are relative to.",
    )
    aparser.add_argument(
        'filename',
        help="File containing JSON-encoded sequence of tests to run.",
    )
    args = aparser.parse_args()
    basedir = args.basedir or os.path.dirname(args.filename)
    builder = UriBuilder(args.baseurl)
    with open(args.filename, encoding='utf-8') as fid:
        source = Source(sequence(json.load(fid)))
    for test in source.next():
        if not args.timeless:
            start = timenow()
        result = drive(os.path.join(basedir, test))
        if not args.timeless:
            end = timenow()
        result['id'] = builder.build(os.path.dirname(test))
        if not args.timeless:
            result['timestamp'] = timestamp(start)
            result['time'] = (end - start).total_seconds()
        print(json.dumps(result))

if __name__ == '__main__':
    main()
