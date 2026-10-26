#!/usr/bin/env python3
"""Check observable detector behavior with isolated synthetic fixtures."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
import check_skill


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'sample-skill'
        self.root.mkdir()

    def write_entry(self, extra=''):
        (self.root / 'SKILL.md').write_text(
            '---\nname: sample-skill\ndescription: Summarize user notes.\n---\nSummarize notes.\n' + extra)

    def codes(self):
        result = check_skill.check(self.root)
        findings = result[0] if isinstance(result, tuple) else result
        return {item['code'] for item in findings}

    def test_missing_entry(self):
        self.assertIn('entry_missing', self.codes())

    def test_clean_entry(self):
        self.write_entry()
        self.assertEqual(self.codes(), set())

    def test_broken_reference_then_fix(self):
        self.write_entry('[Example](example.md)')
        self.assertIn('missing_reference', self.codes())
        (self.root / 'example.md').write_text('Example input and output.')
        self.assertNotIn('missing_reference', self.codes())

    def test_secret_is_flagged_but_never_printed(self):
        self.write_entry()
        value = 'synthetic-credential-for-test-only'
        (self.root / '.env').write_text('password=' + value)
        self.assertIn('possible_secret', self.codes())
        self.assertIn('environment_config', self.codes())
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            with unittest.mock.patch.object(sys, 'argv', ['check_skill.py', str(self.root)]):
                self.assertEqual(check_skill.main(), 0)
        output = stream.getvalue()
        self.assertNotIn(value, output)
        self.assertEqual(json.loads(output)['static_status'], 'ready_for_review')

    def test_external_link(self):
        self.write_entry('[Reference](../outside.md)')
        self.assertIn('external_local_reference', self.codes())

    def test_entry_symlink(self):
        self.write_entry()
        entry = self.root / 'SKILL.md'
        entry.rename(self.root / 'source.md')
        entry.symlink_to(self.root / 'source.md')
        self.assertIn('entry_missing', self.codes())


if __name__ == '__main__':
    import unittest.mock
    unittest.main()
