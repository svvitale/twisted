# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet.main}.
"""

from __future__ import division, absolute_import

import warnings

from twisted.trial import unittest
from twisted.internet.error import ReactorAlreadyInstalledError
from twisted.internet.main import installReactor

from twisted.internet.test.modulehelpers import NoReactor


class TestSSLVersionCheckerTests(unittest.SynchronousTestCase):
    """
    Tests for PyOpenSSL version verification.
    """
    def pyopensslVersionThrowsWarnings(self, versionStr):
        import OpenSSL
        self.patch(OpenSSL.version, '__version__', versionStr)

        with warnings.catch_warnings(record=True) as warningList:
            # Cause import warnings to always be triggered.
            warnings.simplefilter("always", ImportWarning)

            # Import the reactor which in turn will import OpenSSL and check for a compatible version.
            from twisted.internet import reactor
            self.assertTrue(reactor)  # Appease pyflakes

            for warning in warningList:
                if 'Insufficient version of PyOpenSSL' in warning.message.args[0]:
                    # Warning encountered
                    return True

            # Warning not found
            return False

    def test_sufficientVersion(self):
        self.assertFalse(self.pyopensslVersionThrowsWarnings("16.0.0"),
                         "PyOpenSSL warning encountered for a version that we support.")

    def test_insufficientVersion(self):
        self.assertTrue(self.pyopensslVersionThrowsWarnings("0.13"),
                        "PyOpenSSL warning not encountered for a version we do not support.")


class InstallReactorTests(unittest.SynchronousTestCase):
    """
    Tests for L{installReactor}.
    """

    def test_installReactor(self):
        """
        L{installReactor} installs a new reactor if none is present.
        """
        with NoReactor():
            newReactor = object()
            installReactor(newReactor)
            from twisted.internet import reactor
            self.assertIs(newReactor, reactor)


    def test_alreadyInstalled(self):
        """
        If a reactor is already installed, L{installReactor} raises
        L{ReactorAlreadyInstalledError}.
        """
        with NoReactor():
            installReactor(object())
            self.assertRaises(ReactorAlreadyInstalledError, installReactor,
                              object())


    def test_errorIsAnAssertionError(self):
        """
        For backwards compatibility, L{ReactorAlreadyInstalledError} is an
        L{AssertionError}.
        """
        self.assertTrue(issubclass(ReactorAlreadyInstalledError,
                        AssertionError))
