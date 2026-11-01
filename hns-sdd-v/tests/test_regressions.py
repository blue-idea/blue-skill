"""Behavioral regressions for the version lifecycle, references and evidence."""
import unittest

import test_validate_sdd as fixtures
from scripts.validate_sdd import validate_project


class RegressionTest(unittest.TestCase):
    setUp = fixtures.ValidateSddTest.setUp
    tearDown = fixtures.ValidateSddTest.tearDown
    write_registry = fixtures.ValidateSddTest.write_registry
    write_version = fixtures.ValidateSddTest.write_version
    write_core_docs = fixtures.ValidateSddTest.write_core_docs
    def ready(self):
        self.write_registry([('v1', 'finished')])
        v = self.write_version('v1', 'finished')
        self.write_core_docs(v, 'V1')
        self.assertEqual([], validate_project(self.root, 'v1'))
        return v

    def test_empty_core_rejected(self):
        v = self.ready()
        for name in ('requirements.md', 'tasks.md', 'design.md'):
            (v / name).write_text('', encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_evidence_missing_or_failed_rejected(self):
        v = self.ready()
        evidence = v / 'ac/V1-TASK-001-AC.md'
        evidence.unlink()
        self.assertTrue(validate_project(self.root, 'v1'))
        self.write_core_docs(v, 'V1')
        evidence.write_text(evidence.read_text(encoding='utf-8').replace('| PASS |', '| FAIL |'), encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_dangling_and_duplicate_rejected(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('V1-REQ-001', 'V1-REQ-999'), encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))
        self.write_core_docs(v, 'V1')
        p = v / 'requirements.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n## V1-REQ-001\n', encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_status_and_checkbox_must_agree(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('Status**: done', 'Status**: doing'), encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_alignment_is_section_scoped(self):
        v = self.ready()
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8').replace('**Result**: PASS', '**Result**: BLOCKED') + '\n## Other\n- **Result**: PASS\n', encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_default_checks_finished_and_unregistered_directories(self):
        v = self.ready()
        (v / 'tasks.md').unlink()
        self.assertTrue(validate_project(self.root))
        self.write_core_docs(v, 'V1')
        (v.parent / 'v2').mkdir()
        self.assertTrue(validate_project(self.root))

    def test_invalid_dates_rejected(self):
        v = self.ready()
        for p in (v / 'version.md', self.root / 'docs/sdd/versions.md'):
            p.write_text(p.read_text(encoding='utf-8').replace('2026-07-25', 'not-a-date'), encoding='utf-8')
        self.assertTrue(validate_project(self.root))

    def test_explicit_history_reference_allowed(self):
        self.ready()
        self.write_registry([('v1', 'finished'), ('v2', 'active')])
        v = self.write_version('v2', 'active')
        self.write_core_docs(v, 'V2')
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n## Historical dependencies\n- v1/requirements.md\n', encoding='utf-8')
        p = v / 'requirements.md'
        p.write_text(p.read_text(encoding='utf-8') + '\nReferences V1-REQ-001.\n', encoding='utf-8')
        self.assertEqual([], validate_project(self.root))

    def test_candidate_is_read_only(self):
        v = self.ready()
        self.write_registry([('v1', 'active')])
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8').replace('`finished`', '`active`').replace('**Finished**: 2026-07-25', '**Finished**: —'), encoding='utf-8')
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual([], validate_project(self.root, check_finish='v1'))
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_draft_needs_no_design_or_manifest(self):
        self.write_registry([('v1', 'draft')])
        v = self.write_version('v1', 'draft')
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8').split('## Steering Impact Manifest')[0], encoding='utf-8')
        self.assertEqual([], validate_project(self.root))


    def test_product_baseline_candidate_and_history_inheritance(self):
        v = self.ready()
        self.write_registry([('v1', 'active')])
        manifest = ['| V1-IMP-001 | product | add | docs/sdd/current/product.md#login-lockout | requirements.md#v1-req-001 | ac/V1-TASK-001-AC.md | synced |']
        self.write_version('v1', 'active', manifest_rows=manifest)
        product = self.root / 'docs/sdd/current/product.md'
        product.parent.mkdir()
        product.write_text('# Product\n\n## Login lockout\n\nLock after repeated failures.\n', encoding='utf-8')
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n| current/product.md | 已同步 | V1-IMP-001 |\n', encoding='utf-8')
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8') + '\n  - Steering impact: V1-IMP-001\n', encoding='utf-8')
        self.assertEqual([], validate_project(self.root, check_finish='v1'))
        self.assertTrue(validate_project(self.root))
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8').replace('`active`', '`finished`').replace('**Finished**: —', '**Finished**: 2026-07-25'), encoding='utf-8')
        self.write_registry([('v1', 'finished')])
        self.assertEqual([], validate_project(self.root, 'v1'))
        product_before = product.read_bytes()
        self.write_registry([('v1', 'finished'), ('v2', 'active')])
        v2 = self.write_version('v2', 'active')
        self.write_core_docs(v2, 'V2')
        self.assertEqual([], validate_project(self.root))
        self.assertEqual(product_before, product.read_bytes())

    def test_dependency_cycle_rejected(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('Depends on**: none', 'Depends on**: V1-TASK-001'), encoding='utf-8')
        self.assertTrue(validate_project(self.root))

    def test_unbold_unchecked_task_rejected(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('[x] **V1-TASK-001**', '[ ] V1-TASK-001'), encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_missing_anchor_rejected(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('design.md#design', 'design.md#absent'), encoding='utf-8')
        self.assertTrue(validate_project(self.root, 'v1'))

    def test_confirmed_exception_preserves_failed_result(self):
        v = self.ready()
        p = v / 'tasks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('Status**: done', 'Status**: confirmed WONTFIX'), encoding='utf-8')
        p = v / 'ac/V1-TASK-001-AC.md'
        p.write_text(p.read_text(encoding='utf-8').replace('| PASS |', '| FAIL |') + '\n- **Disposition**: confirmed WONTFIX\n- **Confirmed by / date**: fixture user / 2026-07-25\n- **Reason**: accepted fixture limit\n- **Residual risk**: fixture behavior unavailable\n', encoding='utf-8')
        self.assertEqual([], validate_project(self.root, 'v1'))

    def test_baseline_manifest_heading_supported(self):
        v = self.ready()
        p = v / 'version.md'
        p.write_text(p.read_text(encoding='utf-8').replace('Steering Impact Manifest', 'Baseline Impact Manifest'), encoding='utf-8')
        self.assertEqual([], validate_project(self.root, 'v1'))

    def test_cli_reports_failure_without_executing_commands(self):
        import subprocess
        import sys
        from pathlib import Path
        v = self.ready()
        script = Path(__file__).resolve().parents[1] / 'scripts/validate_sdd.py'
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(script), str(self.root), '--finish', 'v1'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        (v / 'tasks.md').write_text('', encoding='utf-8')
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(script), str(self.root)], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(1, result.returncode)


if __name__ == '__main__':
    unittest.main()
