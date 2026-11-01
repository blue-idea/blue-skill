from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_sdd import validate_project


class ValidateSddTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "docs/sdd/specs").mkdir(parents=True)
        (self.root / "docs/sdd/steering").mkdir(parents=True)
        (self.root / "docs/AGENTS.md").write_text("# Agent rules\n", encoding="utf-8")
        for name in ("project-rules.md", "tech-stack.md", "style-guide.md"):
            (self.root / "docs/sdd/steering" / name).write_text(
                f"# {name}\n", encoding="utf-8"
            )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_registry(self, rows: list[tuple[str, str]]) -> None:
        lines = [
            "# SDD Versions",
            "",
            "| Version | Status | Goal | Path | Started | Finished |",
            "|---------|--------|------|------|---------|----------|",
        ]
        for version, status in rows:
            finished = "2026-07-25" if status == "finished" else "—"
            lines.append(
                f"| {version} | {status} | goal | "
                f"`docs/sdd/specs/{version}/` | 2026-07-25 | {finished} |"
            )
        path = self.root / "docs/sdd/versions.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_version(
        self,
        version: str,
        status: str,
        steering_state: str = "未变化",
        manifest_rows: list[str] | None = None,
        steering_overrides: dict[str, str] | None = None,
    ) -> Path:
        version_root = self.root / "docs/sdd/specs" / version
        version_root.mkdir(parents=True, exist_ok=True)
        finished = "2026-07-25" if status == "finished" else "—"
        prefix = version.upper()
        manifest_rows = manifest_rows or []
        sync_states = {
            name: steering_state
            for name in (
                "project-rules.md",
                "tech-stack.md",
                "style-guide.md",
                "data.md",
                "api.md",
            )
        }
        sync_states.update(steering_overrides or {})
        version_root.joinpath("version.md").write_text(
            "\n".join(
                [
                    f"# Version {version}",
                    "",
                    f"- **Version**: `{version}`",
                    f"- **Version Prefix**: `{prefix}`",
                    f"- **Status**: `{status}`",
                    "- **Started**: 2026-07-25",
                    f"- **Finished**: {finished}",
                    "",
                    "## Steering Impact Manifest",
                    "",
                    f"- **No Steering impact**: {'false' if manifest_rows else 'true'}",
                    "",
                    "| Impact ID | Domain | Action | Steering target | Version delta | Verification | State |",
                    "|-----------|--------|--------|-----------------|---------------|--------------|-------|",
                    *manifest_rows,
                    "",
                    "## Alignment review",
                    "",
                    "- **Result**: PASS",
                    "",
                    "## Steering sync",
                    "",
                    "| Document | State | Evidence |",
                    "|----------|-------|----------|",
                    f"| `project-rules.md` | {sync_states['project-rules.md']} | — |",
                    f"| `tech-stack.md` | {sync_states['tech-stack.md']} | — |",
                    f"| `style-guide.md` | {sync_states['style-guide.md']} | — |",
                    f"| `data.md` | {sync_states['data.md']} | — |",
                    f"| `api.md` | {sync_states['api.md']} | — |",
                    "",
                    "## Completion evidence",
                    "",
                    "- Commands and actual results: tests passed",
                    f"- TASK / AC evidence: ac/{prefix}-TASK-001-AC.md",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return version_root

    def write_core_docs(
        self,
        version_root: Path,
        prefix: str,
        include_design: bool = True,
    ) -> None:
        version_root.joinpath("requirements.md").write_text(
            f"# Requirements\n\n## {prefix}-REQ-001\n\n{prefix}-REQ-001-AC-001\n",
            encoding="utf-8",
        )
        if include_design:
            version_root.joinpath("design.md").write_text(
                f"# Design\n\nCovers {prefix}-REQ-001-AC-001\n",
                encoding="utf-8",
            )
        else:
            version_file = version_root.joinpath("version.md")
            version_file.write_text(
                version_file.read_text(encoding="utf-8")
                + "\n## Design decision\n\n- **Design decision**: no new design; follows Steering.\n",
                encoding="utf-8",
            )
        version_root.joinpath("tasks.md").write_text(
            f"# Tasks\n\n- [x] **{prefix}-TASK-001**\n"
            f"  - **REQ**: {prefix}-REQ-001\n  - **AC**: {prefix}-REQ-001-AC-001\n"
            f"  - **Design**: {'design.md#design' if include_design else 'version.md#design-decision'}\n"
            "  - **Test type**: Unit\n  - **Verification command**: python -m unittest\n"
            f"  - **Evidence**: ac/{prefix}-TASK-001-AC.md\n"
            "  - **Depends on**: none\n  - **Status**: done\n",
            encoding="utf-8",
        )
        (version_root / 'ac').mkdir(exist_ok=True)
        (version_root / f'ac/{prefix}-TASK-001-AC.md').write_text(
            '- **Code revision**: fixture-code-1\n- **Spec revision**: fixture-spec-1\n'
            '- **Environment**: isolated fixture\n- **Executed**: 2026-07-25\n'
            '| AC ID | Test type | Command / steps | Expected | Actual | Result | Evidence / error |\n'
            '|-------|-----------|-----------------|----------|--------|--------|------------------|\n'
            f'| {prefix}-REQ-001-AC-001 | Unit | python -m unittest | allowed | allowed | PASS | fixture run |\n',
            encoding='utf-8',
        )

    def test_accepts_one_active_version(self) -> None:
        self.write_registry([("v1", "active")])
        version_root = self.write_version("v1", "active")
        self.write_core_docs(version_root, "V1")

        self.assertEqual([], validate_project(self.root))

    def test_accepts_planned_manifest_before_steering_file_exists(self) -> None:
        self.write_registry([("v1", "active")])
        manifest = [
            "| V1-IMP-001 | data | add | `docs/sdd/steering/data.md#users` | "
            "`data.md#timezone` | — | planned |"
        ]
        version_root = self.write_version(
            "v1",
            "active",
            manifest_rows=manifest,
            steering_overrides={"data.md": "待确认"},
        )
        self.write_core_docs(version_root, "V1")
        version_root.joinpath("data.md").write_text(
            "# Timezone\n\nPlan users.timezone.\n", encoding="utf-8"
        )

        self.assertEqual([], validate_project(self.root))

    def test_rejects_multiple_active_versions(self) -> None:
        self.write_registry([("v1", "active"), ("v2", "active")])
        self.write_version("v1", "active")
        self.write_version("v2", "active")

        errors = "\n".join(validate_project(self.root))
        self.assertIn("同时存在多个 active version", errors)

    def test_rejects_next_version_before_previous_finished(self) -> None:
        self.write_registry([("v1", "active"), ("v2", "draft")])
        self.write_version("v1", "active")
        self.write_version("v2", "draft")

        errors = "\n".join(validate_project(self.root))
        self.assertIn("前一 version 未 finished", errors)

    def test_rejects_wrong_version_prefix(self) -> None:
        self.write_registry([("v1", "active")])
        version_root = self.write_version("v1", "active")
        self.write_core_docs(version_root, "V2")

        errors = "\n".join(validate_project(self.root))
        self.assertIn("ID 前缀必须为 V1-", errors)

    def test_finish_requires_core_docs_closed_tasks_and_resolved_sync(self) -> None:
        self.write_registry([("v1", "finished")])
        version_root = self.write_version("v1", "finished", steering_state="待确认")
        self.write_core_docs(version_root, "V1")
        version_root.joinpath("tasks.md").write_text(
            "# Tasks\n\n- [ ] **V1-TASK-001**\n",
            encoding="utf-8",
        )

        errors = "\n".join(validate_project(self.root, finish_version="v1"))
        self.assertIn("Steering sync 仍有待确认项", errors)
        self.assertIn("仍有未关闭 TASK", errors)

    def test_accepts_finished_version_with_minimal_evidence(self) -> None:
        self.write_registry([("v1", "finished")])
        version_root = self.write_version("v1", "finished")
        self.write_core_docs(version_root, "V1")

        self.assertEqual([], validate_project(self.root, finish_version="v1"))

    def test_accepts_finished_version_without_design_file_when_explained(self) -> None:
        self.write_registry([("v1", "finished")])
        version_root = self.write_version("v1", "finished")
        self.write_core_docs(version_root, "V1", include_design=False)

        self.assertEqual([], validate_project(self.root, finish_version="v1"))

    def test_accepts_synced_data_manifest(self) -> None:
        self.write_registry([("v1", "finished")])
        manifest = [
            "| V1-IMP-001 | data | add | `docs/sdd/steering/data.md#users` | "
            "`data.md#timezone` | `ac/V1-TASK-001-AC.md` | synced |"
        ]
        version_root = self.write_version(
            "v1",
            "finished",
            manifest_rows=manifest,
            steering_overrides={"data.md": "已同步"},
        )
        self.write_core_docs(version_root, "V1")
        tasks_file = version_root / "tasks.md"
        tasks_file.write_text(
            tasks_file.read_text(encoding="utf-8")
            + "\n  - Steering impact: V1-IMP-001\n",
            encoding="utf-8",
        )
        version_root.joinpath("data.md").write_text(
            "# Timezone\n\nAdd users.timezone.\n", encoding="utf-8"
        )
        (self.root / "docs/sdd/steering/data.md").write_text(
            "# Users\n\nIncludes timezone.\n", encoding="utf-8"
        )

        self.assertEqual([], validate_project(self.root, finish_version="v1"))

    def test_finish_rejects_unsynced_manifest_and_sync_mismatch(self) -> None:
        self.write_registry([("v1", "finished")])
        manifest = [
            "| V1-IMP-001 | data | change | `docs/sdd/steering/data.md#users` | "
            "`data.md#timezone` | `ac/V1-TASK-001-AC.md` | verified |"
        ]
        version_root = self.write_version(
            "v1",
            "finished",
            manifest_rows=manifest,
        )
        self.write_core_docs(version_root, "V1")
        tasks_file = version_root / "tasks.md"
        tasks_file.write_text(
            tasks_file.read_text(encoding="utf-8")
            + "\n  - Steering impact: V1-IMP-001\n",
            encoding="utf-8",
        )
        version_root.joinpath("data.md").write_text(
            "# Timezone\n\nChange users.timezone.\n", encoding="utf-8"
        )
        (self.root / "docs/sdd/steering/data.md").write_text(
            "# Users\n", encoding="utf-8"
        )

        errors = "\n".join(validate_project(self.root, finish_version="v1"))
        self.assertIn("Manifest 尚未 synced", errors)
        self.assertIn("data.md 必须标记为 已同步", errors)

    def test_finish_rejects_synced_steering_without_manifest_impact(self) -> None:
        self.write_registry([("v1", "finished")])
        version_root = self.write_version(
            "v1",
            "finished",
            steering_overrides={"api.md": "已同步"},
        )
        self.write_core_docs(version_root, "V1")

        errors = "\n".join(validate_project(self.root, finish_version="v1"))
        self.assertIn("api.md 标记为 已同步，但 Manifest 没有对应 Impact", errors)


if __name__ == "__main__":
    unittest.main()
