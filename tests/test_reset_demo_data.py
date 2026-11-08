"""Destructive reset checks use temporary databases only."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from backend.database import init_db
from scripts.reset_demo_data import reset_data, TABLES


class ResetDemoTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'demo.sqlite3'
        init_db(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute("INSERT INTO conversations VALUES ('c','demo','now','now',0,NULL)")
            c.execute("INSERT INTO messages VALUES ('m','c','user','test','complete',NULL,'unique',NULL,'now','now')")
            c.execute("INSERT INTO messages VALUES ('a','c','assistant','reply','complete',NULL,NULL,'m','now','now')")
            c.execute("INSERT INTO profile_items VALUES ('p','其他','test','self_reported','confirmed','now','now','now')")
            c.execute("INSERT INTO plans VALUES ('main','demo','now')")
            c.execute("INSERT INTO plan_versions (id,plan_id,version_no,status,created_at,updated_at,task_items) VALUES ('v','main',1,'confirmed','now','now','[{\"title\":\"demo\"}]')")

    def test_reset_clears_all_records_but_preserves_schema(self):
        with closing(sqlite3.connect(self.path)) as c, c:
            schema = c.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall()
        before = reset_data(self.path)
        self.assertEqual(before['messages'],2)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertTrue(all(c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] == 0 for t in TABLES))
            self.assertEqual(c.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall(),schema)
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertTrue(all(n==0 for n in reset_data(self.path).values()))

    def test_dry_run_preserves_records_and_pending_blocks_reset(self):
        expected=reset_data(self.path,dry_run=True)
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute("UPDATE messages SET status='pending' WHERE id='m'")
        with self.assertRaisesRegex(ValueError,'待完成'):
            reset_data(self.path)
        self.assertEqual(reset_data(self.path,dry_run=True),expected)

    def test_unknown_schema_and_missing_file_are_not_modified(self):
        with closing(sqlite3.connect(self.path)) as c, c:
            c.execute('CREATE TABLE future_records (id TEXT)')
        with self.assertRaisesRegex(ValueError,'不一致'):
            reset_data(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM messages').fetchone()[0],2)
        missing=self.path.with_name('missing.sqlite3')
        with self.assertRaises(ValueError):reset_data(missing)
        self.assertFalse(missing.exists())
