import sqlite3
import tempfile
import unittest
from pathlib import Path

from bitrix_agent.memory.database import Memory


class MemoryTests(unittest.TestCase):
    def test_schema_and_upsert(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.sqlite3"
            memory = Memory(path)
            memory.experiment("goal", "method.get", {"name": "x"}, result=False, success=True)
            memory.map_item("rest_method", "x", "x", {"available": False})
            memory.map_item("rest_method", "x", "x", {"available": True})
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM bitrix_map").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
