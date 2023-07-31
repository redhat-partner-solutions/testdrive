# testdrive

`testdrive` is a library for:

 * Building a URI for a test case from a base URI and the test case path
 * Generating JUnit test results for supplying to [Red Hat DCI][1] or other CI
 * Generating [Asciidoc][3] test results for human consumption

The implementation of [testdrive.run.main()][2] provides an illustration of how
this library can be used.

## testdrive.run

Module `testdrive.run` is a convenience tool for running a set of tests
specified in a JSON file. Using example files in this repo:

    $ env PYTHONPATH=src python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json
    {"result": false, "reason": "something went wrong", "data": {"foo": "bar"}, "id": "https://github.com/redhat-partner-solutions/testdrive/A/", "timestamp": "2023-07-31T13:29:08.844977+00:00", "time": 0.029334}
    {"result": true, "reason": null, "data": {"baz": 99}, "id": "https://github.com/redhat-partner-solutions/testdrive/B/", "timestamp": "2023-07-31T13:29:08.874374+00:00", "time": 0.02897}
    {"result": false, "reason": "no particular reason", "id": "https://github.com/redhat-partner-solutions/testdrive/C/", "timestamp": "2023-07-31T13:29:08.903396+00:00", "time": 0.003881}

## testdrive.junit

Module `testdrive.junit` can be used to generate JUnit test results from lines
of JSON (one line per test case result):

    $ python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json | \
      python3 -m testdrive.junit --prettify "examples.sequence" -
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-31T13:29:08.844977+00:00" time="0.0623">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.029334">
          <failure type="Failure" message="something went wrong" />
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.02897" />
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.003881">
          <failure type="Failure" message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

## testdrive.xml

Module `testdrive.xml` provides a basic XML validator. This, along with the
schema file `junit/schema/testdrive.xsd`, is provided in order to test the
output from `testdrive.junit` and to allow comparison with Windy Road JUnit
schema `junit/schema/junit.xsd`.

The following JUnit output from testdrive...

    $ cat results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-31T13:29:08.844977+00:00" time="0.0623">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.029334">
          <failure type="Failure" message="something went wrong" />
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.02897" />
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.003881">
          <failure type="Failure" message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

...validates using the testdrive JUnit schema...

    $ python3 -m testdrive.xml junit/schema/testdrive.xsd results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-31T13:29:08.844977+00:00" time="0.0623">
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.029334">
          <failure type="Failure" message="something went wrong" />
        </testcase>
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.02897" />
        <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.003881">
          <failure type="Failure" message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

...and _does not_ validate using the Windy Road JUnit schema:

    $ python3 -m testdrive.xml --verbose junit/schema/junit.xsd results.xml
    failed validating {'tests': '3', 'errors': '0', 'failures': '2', 'skipped': '0'} with XsdAttributeGroup():

    Reason: 'tests' attribute not allowed for element

    Schema:

      <xs:complexType xmlns:xs="http://www.w3.org/2001/XMLSchema">
          <xs:sequence>
              <xs:element name="testsuite" minOccurs="0" maxOccurs="unbounded">
                  <xs:complexType>
                      <xs:complexContent>
                          <xs:extension base="testsuite">
                              <xs:attribute name="package" type="xs:token" use="required">
                                  <xs:annotation>
                                      <xs:documentation xml:lang="en">Derived from testsuite/@name in the non-aggregated documents</xs:documentation>
                                  </xs:annotation>
                              </xs:attribute>
                              <xs:attribute name="id" type="xs:int" use="required">
                                  <xs:annotation>
                                      <xs:documentation xml:lang="en">Starts at '0' for the first testsuite and is incremented by 1 for each following testsuite</xs:documentation>
                                  </xs:annotation>
                              </xs:attribute>
                          </xs:extension>
                      </xs:complexContent>
                  </xs:complexType>
              </xs:element>
          </xs:sequence>
      </xs:complexType>

    Instance:

      <testsuites tests="3" errors="0" failures="2" skipped="0">
        <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-31T13:29:08.844977+00:00" time="0.0623">
          <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.029334">
            <failure type="Failure" message="something went wrong" />
          </testcase>
          <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.02897" />
          <testcase classname="examples.sequence" name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.003881">
            <failure type="Failure" message="no particular reason" />
          </testcase>
        </testsuite>
      </testsuites>

    Path: /testsuites

To see the differences between the schemas, simply use diff:

    $ diff junit/schema/junit.xsd junit/schema/testdrive.xsd
    7c7,16
    < 		<xs:documentation xml:lang="en">JUnit test result schema for the Apache Ant JUnit and JUnitReport tasks
    ---
    > 		<!-- modified: complement original documentation -->
    > 		<xs:documentation xml:lang="en">A schema for testdrive JUnit test results.
    > 
    > testdrive emits test results which are not strictly compatible with the Windy
    > Road JUnit schema (because the CI systems which consume these results are not
    > strictly compatible). This schema is a modified version of the Windy Road JUnit
    > schema, for which the original text in this element is retained below.
    > 
    > -----
    > JUnit test result schema for the Apache Ant JUnit and JUnitReport tasks
    13c22,23
    < 	<xs:simpleType name="ISO8601_DATETIME_PATTERN">
    ---
    > 	<!-- modified: add microseconds and explicit UTC timezone -->
    > 	<xs:simpleType name="ISO8601_DATETIME_UTC">
    15c25
    < 			<xs:pattern value="[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"/>
    ---
    > 			<xs:pattern value="[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+00:00"/>
    25,40c35
    < 					<xs:complexType>
    < 						<xs:complexContent>
    ...

## testdrive.asciidoc

Module `testdrive.asciidoc` can be used to generate [Asciidoc][3] test results
from lines of JSON (one line per test case result):

    $ python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json | \
      python3 -m testdrive.asciidoc "examples.sequence" - | tee results.adoc
    === Test Suite: examples.sequence

    ==== Summary

    [cols=2*.^a]
    |===


    |
    *hostname*
    |
    _not known_

    |
    *started*
    |
    2023-07-31T13:29:08.844977+00:00
    ...

To include this in a simple report:

    $ cat report.adoc
    = Test Report

    :toc:

    == Test Results

    <<<
    include::results.adoc[]

    $ asciidoctor -a toc report.adoc && firefox report.html

[1]: https://www.distributed-ci.io/
[2]: https://github.com/redhat-partner-solutions/testdrive/blob/cce8fb30bd8eed8e83f53665cd1433e20c81cfd3/src/testdrive/run.py#L60
[3]: https://docs.asciidoctor.org/asciidoc/latest/
