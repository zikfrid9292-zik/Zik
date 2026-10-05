import unittest

from bitrix_agent.core.safety import Operation, SafetyViolation, classify_method, require_read


class SafetyTests(unittest.TestCase):
    def test_known_read_allowed(self):
        self.assertEqual(classify_method("tasks.task.list"), Operation.READ)
        require_read("bizproc.workflow.template.list")

    def test_write_delete_and_unknown_fail_closed(self):
        for method in ("tasks.task.add", "task.dependence.delete", "made.up.inspect"):
            with self.subTest(method=method), self.assertRaises(SafetyViolation):
                require_read(method)


if __name__ == "__main__":
    unittest.main()
