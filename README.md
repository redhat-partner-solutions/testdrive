# testdrive

`testdrive` is a library for:

 * Building a URI for a test case based from base URI and the test case path
 * Generating a JUnit file suitable for supplying to [Red Hat DCI][1] or other
   CI

The implementation of [testdrive.run.main()][2] provides an illustration of how
this library can be used.

## testdrive.run

Module `testdrive.run` is also a convenience tool for running a set of tests
specified in a JSON file. The following uses example files in this repo:

    $ env PYTHONPATH=src python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json
    {"result": false, "reason": "something went wrong", "data": {"foo": "bar"}, "id": "https://github.com/redhat-partner-solutions/testdrive/A/", "timestamp": "2023-07-27T15:48:52.376983+00:00", "time": 0.028625}
    {"result": true, "reason": null, "data": {"baz": 99}, "id": "https://github.com/redhat-partner-solutions/testdrive/B/", "timestamp": "2023-07-27T15:48:52.405772+00:00", "time": 0.065822}
    {"result": false, "reason": "no particular reason", "id": "https://github.com/redhat-partner-solutions/testdrive/C/", "timestamp": "2023-07-27T15:48:52.471740+00:00", "time": 0.006504}

## testdrive.junit

Module `testdrive.junit` can be used to generate a JUnit file from lines of
JSON (one line per test case result):

    $ python3 -m testdrive.run https://github.com/redhat-partner-solutions/testdrive/ examples/sequence/tests.json | \
      python3 -m testdrive.junit --prettify "examples.sequence" -
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-27T16:18:15.986502+00:00" time="0.121763">
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.045674">
          <failure message="something went wrong" />
        </testcase>
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.068546" />
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.007399">
          <failure message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

## testdrive.xml

Module `testdrive.xml` provides a basic XML validator. This, along with the
schema file `junit/schema/testdrive.xsd`, are provided in order to test the
output from `testdrive.junit` and for comparison with `junit/schema/junit.xsd`.

The following JUnit output from testdrive...

    $ cat results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-27T16:18:15.986502+00:00" time="0.121763">
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.045674">
          <failure message="something went wrong" />
        </testcase>
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.068546" />
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.007399">
          <failure message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

...validates using the testdrive JUnit schema...

    $ python3 -m testdrive.xml junit/schema/testdrive.xsd results.xml
    <?xml version='1.0' encoding='utf-8'?>
    <testsuites tests="3" errors="0" failures="2" skipped="0">
      <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-27T16:18:15.986502+00:00" time="0.121763">
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.045674">
          <failure message="something went wrong" />
        </testcase>
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.068546" />
        <testcase name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.007399">
          <failure message="no particular reason" />
        </testcase>
      </testsuite>
    </testsuites>

...and _does not validate_ using the Windy Road JUnit schema:

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
        <testsuite name="examples.sequence" tests="3" errors="0" failures="2" skipped="0" timestamp="2023-07-27T16:18:15.986502+00:00" time="0.121763">
          <testcase name="https://github.com/redhat-partner-solutions/testdrive/A/" time="0.045674">
            <failure message="something went wrong" />
          </testcase>
          <testcase name="https://github.com/redhat-partner-solutions/testdrive/B/" time="0.068546" />
          <testcase name="https://github.com/redhat-partner-solutions/testdrive/C/" time="0.007399">
            <failure message="no particular reason" />
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

[1]: https://www.distributed-ci.io/
[2]: https://github.com/redhat-partner-solutions/testdrive/blob/cce8fb30bd8eed8e83f53665cd1433e20c81cfd3/src/testdrive/run.py#L60
