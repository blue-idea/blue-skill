"""Packaging checks; lifecycle behavior is exercised by regression tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTest(unittest.TestCase):
    def test_frontmatter_and_routes_resolve(self):
        entry = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertRegex(entry, r'^---\nname: hns-sdd\ndescription: .+\n---')
        routes = re.findall(r'(?:phases|references)/[\w-]+\.md', entry)
        self.assertTrue(routes)
        for route in routes:
            self.assertTrue((ROOT / route).is_file(), route)

    def test_templates_are_available_for_actual_artifacts(self):
        for name in ('agents', 'versions', 'version', 'current', 'steering', 'requirements', 'design', 'tasks', 'ac_matrix'):
            self.assertTrue((ROOT / f'templates/tpl_{name}.md').is_file())

    def test_active_instructions_do_not_route_to_legacy_paths(self):
        paths = [ROOT / 'SKILL.md', ROOT / 'readme.md', *list((ROOT / 'templates').glob('*.md')), *list((ROOT / 'phases').glob('0*.md'))]
        for path in paths:
            self.assertNotIn('docs/spec/', path.read_text(encoding='utf-8'), str(path))


if __name__ == '__main__':
    unittest.main()
