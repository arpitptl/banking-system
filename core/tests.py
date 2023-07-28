from django.test.runner import DiscoverRunner
from .tests.test_suite import account_test_suite


class AccountTestRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        suite = account_test_suite()
        return suite.run_tests(test_labels, extra_tests=extra_tests, **kwargs)
