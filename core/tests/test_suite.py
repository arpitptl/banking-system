# accounts/tests/test_suite.py

import unittest
from .test_models import AccountModelTestCase
from .test_views import CreateAccountAPITestCase


def account_test_suite():
    suite = unittest.TestSuite()
    suite.addTest(AccountModelTestCase())
    suite.addTest(CreateAccountAPITestCase())
    return suite
