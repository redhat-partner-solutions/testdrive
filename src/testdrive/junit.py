### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate JUnit output"""

import sys
from contextlib import nullcontext
from argparse import ArgumentParser
import json

from xml.etree import ElementTree as ET

def open_input(filename, encoding='utf-8', **kwargs):
    """Return a context manager for reading from `filename`.

    If `filename` is '-' then read from stdin instead of `filename`.
    """
    if filename == '-':
        return nullcontext(sys.stdin)
    return open(filename, encoding=encoding, **kwargs)

def _buildattrs(**kwargs):
    """Return a dict from `kwargs` suitable for creating an XML element with."""
    attrs = {}
    for (key, val) in kwargs.items():
        if val is not None:
            attrs[key] = str(val)
    return attrs

def _testsuites(
        tests, errors, failures, skipped=0,
        time=None,
    ):
    """Return XML testsuites element, root element.

    `tests` is the number of tests run;
    `errors` the number of tests which did not return a result;
    `failures` the number of tests which returned a failure result;
    `skipped` the number of tests not run;
    `time` the elapsed time to run all tests.
    """
    attrs = _buildattrs(
        tests=tests, errors=errors, failures=failures, skipped=skipped,
        time=time,
    )
    return ET.Element('testsuites', attrs)

def _testsuite(
        suite,
        tests, errors, failures, skipped=0,
        hostname=None,
        timestamp=None, time=None,
    ): # pylint: disable=too-many-arguments
    """Return XML testsuite element, a container for test cases.

    `suite` is the name of the test suite.
    `tests` is the number of tests run;
    `errors` the number of tests which did not return a result;
    `failures` the number of tests which returned a failure result;
    `skipped` the number of tests not run;
    `hostname` the name of the host which ran the tests;
    `timestamp` the ISO 8601 datetime when the suite was run;
    `time` the elapsed time to run all tests.
    """
    attrs = _buildattrs(
        name=suite,
        tests=tests, errors=errors, failures=failures, skipped=skipped,
        hostname=hostname,
        timestamp=timestamp, time=time,
    )
    return ET.Element('testsuite', attrs)

def _testcase(
        uri, error=None, failure=None,
        time=None,
    ):
    """Return XML testcase element, for test case success, failure or error.

    `uri` is the URI of the test case;
    `error` is the error reason;
    `failure` is the failure reason;
    `time` the elapsed time to run the test.

    Supplying neither `error` nor `failure` implies test success. If both
    `error` and `failure` are supplied, `failure` is ignored.
    """
    attrs = _buildattrs(
        classname=None, ### TODO
        name=uri,
        time=time,
    )
    e_case = ET.Element('testcase', attrs)
    if error is not None:
        message = error.split('\n', 1)[0]
        e_error = ET.Element('error', {'message': message})
        e_case.append(e_error)
    elif failure is not None:
        message = failure.split('\n', 1)[0]
        e_failure = ET.Element('failure', {'message': message})
        e_case.append(e_failure)
    return e_case

def junit(suite, cases, hostname=None, prettify=False):
    """Return JUnit output for test `cases` in `suite`.

    `suite` is the string name of the test suite;
    `cases` is a sequence of dict, with each dict defining test case result and
    metadata;
    `hostname` the name of the host which ran the tests;
    if `prettify` then indent XML output.
    """
    tests = len(cases)
    failures = sum(1 for case in cases if case['result'] is False)
    errors = sum(1 for case in cases if case['result'] == 'error')
    e_root = _testsuites(tests, errors, failures)
    e_suite = _testsuite(suite, tests, errors, failures, hostname=hostname)
    for case in cases:
        if case['result'] is True:
            e_case = _testcase(case['id'])
        elif case['result'] is False:
            e_case = _testcase(case['id'], failure=case['reason'])
        elif case['result'] == 'error':
            e_case = _testcase(case['id'], error=case['reason'])
        else:
            raise ValueError(
                f"""bad result "{case['result']}" for case {case['id']}"""
            )
        e_suite.append(e_case)
    e_root.append(e_suite)
    if prettify:
        ET.indent(e_root)
    return ET.tostring(e_root, encoding='unicode', xml_declaration=True)

def main():
    """Generate JUnit output for test cases.

    Build JUnit output for the test cases in input. Print the JUnit output to
    stdout. Each line of input must contain a JSON object specifying the test
    id, result and other metadata for a single test case.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '--hostname',
        help=' '.join((
            "The name of the host which ran the tests.",
            "(Used in JUnit output when supplied.)",
        )),
    )
    aparser.add_argument(
        '--prettify', action='store_true',
        help="pretty print XML output",
    )
    aparser.add_argument(
        'suite',
        help="The name of the test suite. (Used in JUnit output.)",
    )
    aparser.add_argument(
        'input',
        help="input file, or '-' to read from stdin",
    )
    args = aparser.parse_args()
    with open_input(args.input) as fid:
        cases = tuple(json.loads(line) for line in fid)
    print(junit(args.suite, cases, args.hostname, args.prettify))

if __name__ == '__main__':
    main()
