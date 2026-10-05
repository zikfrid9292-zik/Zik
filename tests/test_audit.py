import unittest

from bitrix_agent.core.audit import sanitize


class AuditTests(unittest.TestCase):
    def test_nested_secrets_are_redacted(self):
        value = sanitize({"webhook": "secret", "nested": [{"api_key": "secret"}], "name": "Test"})
        self.assertEqual(value["webhook"], "<redacted>")
        self.assertEqual(value["nested"][0]["api_key"], "<redacted>")
        self.assertEqual(value["name"], "Test")


if __name__ == "__main__":
    unittest.main()
