import importlib.util
import unittest
from pathlib import Path

class AspectPatternsTests(unittest.TestCase):
    def test_cs_pattern_action_matches_all_archived_models(self):
        path = Path(__file__).resolve().parents[1] / 'tools' / 'verify_aspect_patterns.py'
        self.assertTrue(path.exists(), 'Missing verifier for the CS pattern action')
        spec = importlib.util.spec_from_file_location('aspect_patterns', path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result['direction_action_checks'], 112)
        self.assertEqual(result['rational_switch_checks'], 64)
        self.assertEqual(result['nality_pair_checks'], 128)
        self.assertEqual(result['other_directions_fixed'], [1, 6, 7])
        self.assertTrue(result['all_checks_passed'])

if __name__ == '__main__':
    unittest.main()
