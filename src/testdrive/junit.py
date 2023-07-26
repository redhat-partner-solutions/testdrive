### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate JUnit output"""

import sys
from contextlib import nullcontext
from argparse import ArgumentParser
import json

from xml.etree import ElementTree as ET

from .run import timevalue

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
        uri,
        error=None, failure=None,
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
        classname=None, ### TODO? appears in example JUnit files
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

def _time_attr_values(cases):
    """Return (timestamp, time_total) for test `cases`.

    If `cases` contain no timing information return (None, None). Otherwise
    return the ISO 8601 string for the earliest timestamp in `cases` for
    `timestamp`; the total number of seconds from this timestamp to the end of
    test execution for `time_total`.
    """
    # result variables
    timestamp = time_total = None
    # working variables
    tv_start = tv_end = time_last = None
    for case in cases:
        if 'timestamp' in case:
            tv_case = timevalue(case['timestamp'])
            if tv_start is None:
                timestamp = case['timestamp']
                tv_start = tv_end = tv_case
                time_last = case['time']
            elif tv_case < tv_start:
                timestamp = case['timestamp']
                tv_start = tv_case
            elif tv_end < tv_case:
                tv_end = tv_case
                time_last = case['time']
    if tv_start is not None:
        time_total = (tv_end - tv_start).total_seconds() + time_last
        time_total = round(time_total, 6)
    return (timestamp, time_total)

def junit(suite, cases, hostname=None, prettify=False):
    """Return JUnit output for test `cases` in `suite`.

    `suite` is the string name of the test suite;
    `cases` is a sequence of dict, with each dict defining test case result and
    metadata;
    `hostname` the name of the host which ran the tests;
    if `prettify` then indent XML output.

    Each case must supply values for keys:
        id - the test URI
        result - a boolean test result or "error" (no result produced)
        reason - string reason describing test failure or error

    Each case may supply values for keys:
        timestamp - ISO 8601 string of UTC time when the test was started
        time - test duration in seconds

    If `timestamp` is supplied then `time` must also be supplied.
    """
    tests = len(cases)
    errors = sum(1 for case in cases if case['result'] == 'error')
    failures = sum(1 for case in cases if case['result'] is False)
    (timestamp, time_total) = _time_attr_values(cases)
    e_root = _testsuites(tests, errors, failures)
    e_suite = _testsuite(
        suite,
        tests, errors, failures,
        hostname=hostname,
        timestamp=timestamp, time=time_total,
    )
    for case in cases:
        kwargs = {'time': case.get('time')}
        if case['result'] is False:
            kwargs['failure'] = case['reason']
        elif case['result'] == 'error':
            kwargs['error'] = case['reason']
        elif case['result'] is not True:
            raise ValueError(
                f"""bad result "{case['result']}" for case {case['id']}"""
            )
        e_case = _testcase(case['id'], **kwargs)
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