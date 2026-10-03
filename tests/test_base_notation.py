"""Checks for the agreed partial-symbol notation in working chapters."""
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / 'formalization' / 'base'

class PartialNotationTests(unittest.TestCase):
    def test_working_chapters_use_partial_for_dichotomies(self):
        for path in BASE.glob('*.md'):
            text = path.read_text(encoding='utf-8')
            self.assertNotIn(r'\operatorname{dich', text, path.name)
        main = (BASE / '01-hadamard-and-correspondence.md').read_text(encoding='utf-8')
        for carrier in ('I', 'F', 'T'):
            self.assertIn(r'\partial_c^{' + carrier + '}', main)
        self.assertIn('оператор дифференцирования', main)
        self.assertIn('номер столбца', main)

if __name__ == '__main__':
    unittest.main()
