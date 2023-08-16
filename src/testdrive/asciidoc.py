### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate asciidoc output"""

from argparse import ArgumentParser
import json

from .cases import summarize
from .common import open_input

def row(*cells):
    """Return a string for an asciidoc table row with `cells`."""
    return '\n|\n' + '\n|\n'.join((str(c) for c in cells))

def asciidoc(suite, cases, hostname=None):
    """Return asciidoc output for test `cases` in `suite`.

    `suite` is the string name of the test suite;
    `cases` is a sequence of dict, with each dict defining test case result and
    metadata;
    `hostname` the name of the host which ran the tests.

    Each case must supply values for keys:
        id - the test URI
        result - a boolean test result or "error" (no result produced)
        reason - string reason describing test failure or error

    Each case may supply values for keys:
        timestamp - ISO 8601 string of UTC time when the test was started
        time - test duration in seconds

    If `timestamp` is supplied then `time` must also be supplied.
    """
    summary = summarize(cases)
    lines = [
        f'== Test Suite: {suite}',
        '',
        '==== Summary',
        '',
        '[cols=2*.^a]',
        '|===',
        '',
        row('*hostname*', hostname or "_not known_"),
        row('*started*', summary["timestamp"]),
        row('*duration (s)*', summary["duration"]),
        row('*test cases*', summary["total"]),
        row('*test error*', summary["error"]),
        row('*test failure*', summary["failure"]),
        row('*test success*', summary["success"]),
        '|===',
        '',
        '==== Results',
        '',
        '[%header,cols=5*.^a]',
        '|===',
        '|id|timestamp|duration (s)|result|reason',
        '',
    ]
    for case in cases:
        if case['result'] is True:
            result = 'success'
        elif case['result'] is False:
            result = 'failure'
        else:
            result = case['result']
        lines.append(row(
            case['id'],
            case.get('timestamp', '_not known_'),
            case.get('time', '_not known_'),
            result,
            case['reason'] or '',
        ))
    lines.append('|===')
    return '\n'.join(lines)

def main():
    """Generate asciidoc for test cases.

    Each line of input must contain a JSON object specifying the test id, result
    and other metadata for a single test case.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '--hostname',
        help=' '.join((
            "The name of the host which ran the tests.",
            "(Used in asciidoc output when supplied.)",
        )),
    )
    aparser.add_argument(
        'suite',
        help="The name of the test suite. (Used in asciidoc output.)",
    )
    aparser.add_argument(
        'input',
        help="input file, or '-' to read from stdin",
    )
    args = aparser.parse_args()
    with open_input(args.input) as fid:
        cases = tuple(json.loads(line) for line in fid)
    print(asciidoc(args.suite, cases, args.hostname))

if __name__ == '__main__':
    main()
