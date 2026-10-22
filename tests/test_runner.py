import unittest
from scripts.run_tests import evaluate_run


class RunnerTests(unittest.TestCase):
    def test_success_marker_after_expected_timeout_is_accepted(self):
        self.assertTrue(evaluate_run('Test 3 - SRT Preemption: PASSED', None))

    def test_success_does_not_hide_a_failure_elsewhere_in_the_log(self):
        self.assertFalse(evaluate_run('TEST PASSED\nDEADLINE ENFORCEMENT FAILED', None))

    def test_kernel_fault_is_not_a_success(self):
        self.assertFalse(evaluate_run('PASSED\nqemu: fatal: Lockup: cannot escalate', None))

    def test_unexpected_process_failure_is_not_a_success(self):
        self.assertFalse(evaluate_run('PASSED', 1))

    def test_timeout_without_a_result_is_not_a_success(self):
        self.assertFalse(evaluate_run('Starting scheduler...', None))
