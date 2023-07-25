### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for testdrive.uri"""

from unittest import TestCase

from testdrive.uri import UriBuilder

class TestUrn(TestCase):
    """Tests for testdrive.uri.UriBuilder building URN"""
    def test_urn_base_errors(self):
        """Test testdrive.uri.UriBuilder base URN errors"""
        with self.assertRaises(ValueError):
            UriBuilder('urn:path?query=not-allowed')
        with self.assertRaises(ValueError):
            UriBuilder('urn:path#fragment-not-allowed')
        with self.assertRaises(ValueError):
            UriBuilder('urn:path#') # empty fragment not allowed
    def test_urn_path_rel(self):
        """Test testdrive.uri.UriBuilder builds URN from relative path"""
        base = 'urn:abc:def'
        path = 'foo/bar'
        qargs = {'v': 1}
        for b_suffix in ('', ':'):
            for p_suffix in ('', '/'):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    'urn:abc:def:foo:bar',
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    'urn:abc:def:foo:bar?v=1',
                )
    def test_urn_path_abs(self):
        """Test testdrive.uri.UriBuilder builds URN from absolute path"""
        base = 'urn:ghi'
        path = '/quux/corge'
        qargs = {'v': 2}
        for b_suffix in ('', ':'):
            for p_suffix in ('', '/'):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    'urn:ghi:quux:corge',
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    'urn:ghi:quux:corge?v=2',
                )

class TestUrl(TestCase):
    """Tests for testdrive.uri.UriBuilder building URL"""
    def test_url_base_errors(self):
        """Test testdrive.uri.UriBuilder base URL errors"""
        with self.assertRaises(ValueError):
            UriBuilder('//authority/path/') # missing scheme not allowed
        with self.assertRaises(ValueError):
            UriBuilder('scheme://authority/path?query=not-allowed')
        with self.assertRaises(ValueError):
            UriBuilder('scheme://authority/path#fragment-not-allowed')
        with self.assertRaises(ValueError):
            UriBuilder('scheme://authority/path#') # empty fragment not allowed
    def test_url_path_rel(self):
        """Test testdrive.uri.UriBuilder builds URL from relative path"""
        base = 'https://abc.org/def'
        path = 'foo/bar'
        qargs = {'v': 3}
        for b_suffix in ('', '/'):
            for p_suffix in ('', '/'):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    'https://abc.org/def/foo/bar/',
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    'https://abc.org/def/foo/bar/?v=3',
                )
    def test_url_path_abs(self):
        """Test testdrive.uri.UriBuilder builds URL from absolute path"""
        base = 'https://ghi.org'
        path = '/quux/corge'
        qargs = {'v': 'thud'}
        for b_suffix in ('', '/'):
            for p_suffix in ('', '/'):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    'https://ghi.org/quux/corge/',
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    'https://ghi.org/quux/corge/?v=thud',
                )
