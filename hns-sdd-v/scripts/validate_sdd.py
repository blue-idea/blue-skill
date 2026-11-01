from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


VERSION_RE = re.compile(r"^v([1-9][0-9]*)$")
ID_RE = re.compile(
    r"\bV[1-9][0-9]*-(?:REQ|TASK)-[0-9]{3}(?:-AC-[0-9]{3})?\b",
    re.IGNORECASE,
)
IMPACT_ID_RE = re.compile(r"\bV[1-9][0-9]*-IMP-[0-9]{3}\b", re.IGNORECASE)
ALLOWED_STATUS = {"draft", "active", "finished"}
RESOLVED_SYNC = {"未变化", "已同步", "不适用"}
MANIFEST_DOMAINS = {
    "product": "product.md",
    "project-rules": "project-rules.md",
    "tech-stack": "tech-stack.md",
    "style-guide": "style-guide.md",
    "data": "data.md",
    "api": "api.md",
}
MANIFEST_ACTIONS = {"add", "change", "deprecate", "remove"}
MANIFEST_STATES = {"planned", "verified", "synced"}
STEERING_FILES = (
    "project-rules.md",
    "tech-stack.md",
    "style-guide.md",
    "data.md",
    "api.md",
)
CORE_FILES = ("requirements.md", "tasks.md")
SCANNED_FILES = (
    "requirements.md",
    "design.md",
    "tasks.md",
    "analysis-report.md",
    "test_strategy.md",
    "traceability.md",
    "data.md",
    "api.md",
)


def _section(text: str, title: str) -> str:
    match = re.search(rf"(?im)^##\s+{re.escape(title)}\s*$", text)
    if not match:
        return ""
    tail = text[match.end():]
    return re.split(r"(?m)^##\s+", tail, maxsplit=1)[0]


def _date(value: str | None) -> bool:
    try:
        return bool(value and date.fromisoformat(value).isoformat() == value)
    except ValueError:
        return False


def _local_link(root: Path, link: str) -> list[str]:
    """Resolve a local Markdown file and optional GitHub-style heading anchor."""
    path, _, anchor = link.strip().strip('`').partition('#')
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        return [f"引用文件不存在或越界：{link}"]
    if anchor:
        text = target.read_text(encoding='utf-8')
        anchors = set(re.findall(r'<a\s+id=[\"\']([^\"\']+)', text))
        counts: Counter[str] = Counter()
        for heading in re.findall(r'(?m)^#{1,6}\s+(.+?)\s*#*$', text):
            slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
            index = counts[slug]
            counts[slug] += 1
            anchors.add(slug + (f'-{index}' if index else ''))
        if anchor not in anchors:
            return [f"引用锚点不存在：{link}"]
    return []


def _declarations(root: Path) -> list[str]:
    req = root / 'requirements.md'
    task = root / 'tasks.md'
    ids = []
    if req.is_file():
        text = req.read_text(encoding='utf-8')
        ids += re.findall(r'(?m)^##\s+(V\d+-REQ-\d{3})\b', text)
        ids += re.findall(r'(?m)^\s*(?:-\s*id:\s*|)(V\d+-REQ-\d{3}-AC-\d{3})\s*$', text)
    if task.is_file():
        ids += [item[1] for item in _task_blocks(task.read_text(encoding='utf-8'))]
    return ids


def _task_blocks(text: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(r'(?m)^\s*-\s*\[([ xX])\]\s*(?:\*\*)?(V\d+-TASK-\d{3})\b[^\n]*')
    matches = list(pattern.finditer(text))
    return [(m.group(1), m.group(2), text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)]) for i, m in enumerate(matches)]


def _graph_errors(root: Path, version: str, *, finish: bool = False) -> list[str]:
    errors = []
    ids = _declarations(root)
    for identifier, count in Counter(ids).items():
        if count > 1:
            errors.append(f"重复声明：{identifier}")
        if not identifier.startswith(version.upper() + '-'):
            errors.append(f"ID 前缀必须为 {version.upper()}-：{identifier}")
    reqs = {i for i in ids if '-REQ-' in i and '-AC-' not in i}
    acs = {i for i in ids if '-AC-' in i}
    tasks = root / 'tasks.md'
    blocks = _task_blocks(tasks.read_text(encoding='utf-8')) if tasks.is_file() else []
    if finish and (not reqs or not acs or not blocks):
        errors.append('完成门要求非空 REQ、AC 与 TASK 声明')
    for req in reqs:
        if not any(ac.startswith(req + '-AC-') for ac in acs):
            errors.append(f'REQ 缺少 AC：{req}')
    for ac in acs:
        if ac.rsplit('-AC-', 1)[0] not in reqs:
            errors.append(f'AC 缺少所属 REQ：{ac}')
    covered = set()
    dependencies = {}
    for checked, identifier, body in blocks:
        task_acs = set(re.findall(r'V\d+-REQ-\d{3}-AC-\d{3}', _metadata(body, 'AC') or ''))
        covered |= task_acs
        dependencies[identifier] = set(re.findall(r'V\d+-TASK-\d{3}', _metadata(body, 'Depends on') or ''))
        if not finish:
            continue
        status = _metadata(body, 'Status')
        if status not in {'done', 'confirmed BLOCKED', 'confirmed WONTFIX'} or checked.lower() != 'x':
            errors.append(f'仍有未关闭 TASK 或状态不一致：{identifier}')
        for field in ('REQ', 'AC', 'Design', 'Test type', 'Verification command', 'Evidence', 'Depends on', 'Status'):
            if not _metadata(body, field):
                errors.append(f'{identifier} 缺少 {field}')
        if not task_acs or not task_acs <= acs:
            errors.append(f'{identifier} AC 绑定缺失或悬空')
        task_reqs = set(re.findall(r'V\d+-REQ-\d{3}', _metadata(body, 'REQ') or ''))
        if not task_reqs <= reqs or not {ac.rsplit('-AC-', 1)[0] for ac in task_acs} <= task_reqs:
            errors.append(f'{identifier} REQ 与 AC 归属不一致')
        if _metadata(body, 'Test type') not in {'Unit', 'Integration', 'Contract', 'API', 'E2E', 'Performance', 'Security', 'Manual'}:
            errors.append(f'{identifier} Test type 非法')
        design = _metadata(body, 'Design')
        if design:
            errors.extend(_local_link(root, design))
        evidence = _metadata(body, 'Evidence')
        if evidence:
            link_errors = _local_link(root, evidence)
            errors.extend(link_errors)
            if not link_errors:
                report = (root / evidence.split('#')[0]).read_text(encoding='utf-8')
                for field in ('Code revision', 'Spec revision', 'Environment', 'Executed'):
                    if not _metadata(report, field):
                        errors.append(f'{identifier} 证据缺少 {field}')
                if not _date(_metadata(report, 'Executed')) or '{{' in report:
                    errors.append(f'{identifier} 证据日期非法或仍有占位符')
                results = {}
                for line in report.splitlines():
                    cells = [_strip_cell(c) for c in line.strip().strip('|').split('|')]
                    if cells and cells[0] in task_acs:
                        if cells[0] in results:
                            errors.append(f'{identifier} 重复 AC 结果：{cells[0]}')
                        results[cells[0]] = cells[5] if len(cells) == 7 and all(cells) else ''
                if set(results) != task_acs or any(r not in {'PASS', 'FAIL', 'BLOCKED'} for r in results.values()):
                    errors.append(f'{identifier} AC 证据不完整或结果非法')
                if status == 'done' and any(r != 'PASS' for r in results.values()):
                    errors.append(f'{identifier} AC 未全部 PASS')
                if status in {'confirmed BLOCKED', 'confirmed WONTFIX'}:
                    for field in ('Confirmed by / date', 'Reason', 'Residual risk'):
                        value = _metadata(report, field)
                        if not value or value in {'none', '—', '-'}:
                            errors.append(f'{identifier} 例外缺少 {field}')
                    if _metadata(report, 'Disposition') != status:
                        errors.append(f'{identifier} 例外处置不一致')
    if finish and acs - covered:
        errors.append(f'AC 未被 TASK 覆盖：{sorted(acs - covered)}')
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            errors.append(f'TASK 依赖环：{node}')
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in dependencies.get(node, set()):
            if dep not in dependencies:
                errors.append(f'TASK 依赖不存在：{dep}')
            else:
                visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in dependencies:
        visit(node)
    return errors


@dataclass(frozen=True)
class ImpactRow:
    impact_id: str
    domain: str
    action: str
    target: str
    delta: str
    verification: str
    state: str


@dataclass(frozen=True)
class VersionRow:
    version: str
    status: str
    path: str
    started: str
    finished: str

    @property
    def number(self) -> int:
        match = VERSION_RE.fullmatch(self.version)
        return int(match.group(1)) if match else -1


def _strip_cell(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def _parse_registry(path: Path) -> tuple[list[VersionRow], list[str]]:
    if not path.is_file():
        return [], [f"缺少版本注册表：{path}"]

    lines = path.read_text(encoding="utf-8").splitlines()
    table_rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [_strip_cell(cell) for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        table_rows.append(cells)

    if not table_rows:
        return [], ["versions.md 中缺少版本表格"]

    header = [cell.lower() for cell in table_rows[0]]
    required = {"version", "status", "path", "started", "finished"}
    if not required.issubset(header):
        missing = ", ".join(sorted(required - set(header)))
        return [], [f"versions.md 表头缺少字段：{missing}"]

    index = {name: header.index(name) for name in required}
    rows: list[VersionRow] = []
    errors: list[str] = []
    for cells in table_rows[1:]:
        if not any(cells):
            continue
        if len(cells) < len(header):
            errors.append(f"versions.md 表格行列数不足：{' | '.join(cells)}")
            continue
        rows.append(
            VersionRow(
                version=cells[index["version"]],
                status=cells[index["status"]],
                path=cells[index["path"]].replace("\\", "/"),
                started=cells[index["started"]],
                finished=cells[index["finished"]],
            )
        )
    return rows, errors


def _metadata(text: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^[ \t]*-[ \t]*\*\*{re.escape(field)}\*\*:[ \t]*`?([^`\r\n]+?)`?[ \t]*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _parse_manifest(text: str) -> tuple[str | None, list[ImpactRow], list[str]]:
    section_match = re.search(
        r"(?ims)^##\s+(?:Steering|Baseline) Impact Manifest\s*$\n(.*?)(?=^##\s|\Z)",
        text,
    )
    if not section_match:
        return None, [], ["缺少 Steering Impact Manifest"]

    section = section_match.group(1)
    no_impact = _metadata(section, "No Steering impact")
    rows: list[ImpactRow] = []
    errors: list[str] = []
    header_found = False
    for line in section.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [_strip_cell(cell) for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        if cells[0].lower() == "impact id":
            header_found = True
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        if not header_found:
            continue
        if len(cells) != 7:
            errors.append(f"Steering Impact Manifest 行列数必须为 7：{' | '.join(cells)}")
            continue
        rows.append(ImpactRow(*cells))

    if not header_found:
        errors.append("Steering Impact Manifest 缺少标准表头")
    return no_impact, rows, errors


def _manifest_errors(
    project_root: Path,
    row: VersionRow,
    version_text: str,
    *,
    for_finish: bool = False,
    candidate: bool = False,
    check_targets: bool = True,
) -> tuple[list[str], list[ImpactRow]]:
    no_impact, impacts, errors = _parse_manifest(version_text)
    if no_impact not in {"true", "false"}:
        errors.append("No Steering impact 必须为 true 或 false")
    if no_impact == "true" and impacts:
        errors.append("No Steering impact 为 true 时不得存在 Manifest 数据行")
    if no_impact == "false" and not impacts:
        errors.append("No Steering impact 为 false 时至少需要一条 Manifest 数据行")

    expected_prefix = row.version.upper()
    seen: set[str] = set()
    version_root = project_root / "docs/sdd/specs" / row.version
    for impact in impacts:
        if impact.impact_id in seen:
            errors.append(f"Impact ID 重复：{impact.impact_id}")
        seen.add(impact.impact_id)
        expected_id = re.fullmatch(
            rf"{re.escape(expected_prefix)}-IMP-[0-9]{{3}}", impact.impact_id
        )
        if not expected_id:
            errors.append(
                f"{row.version} Impact ID 前缀必须为 {expected_prefix}-IMP-：{impact.impact_id}"
            )
        if impact.domain not in MANIFEST_DOMAINS:
            errors.append(f"Impact Domain 非法：{impact.domain}")
        if impact.action not in MANIFEST_ACTIONS:
            errors.append(f"Impact Action 非法：{impact.action}")
        if impact.state not in MANIFEST_STATES:
            errors.append(f"Impact State 非法：{impact.state}")
        if impact.state == "synced" and row.status != "finished" and not candidate:
            errors.append(f"active/draft version 的 Manifest 不得 synced：{impact.impact_id}")
        if for_finish and impact.state != "synced":
            errors.append(f"Manifest 尚未 synced：{impact.impact_id}")

        target = impact.target.strip()
        target_match = re.fullmatch(r"docs/sdd/(steering|current)/([^/#]+\.md)#(.+)", target)
        expected_file = MANIFEST_DOMAINS.get(impact.domain)
        if not target_match:
            errors.append(
                f"Impact Steering target 必须是 docs/sdd/steering/<file>.md#anchor：{impact.impact_id}"
            )
        elif expected_file and (target_match.group(2) != expected_file or target_match.group(1) != ('current' if impact.domain == 'product' else 'steering')):
            errors.append(
                f"{impact.impact_id} 的 Steering target 与 Domain 不一致：应为 {expected_file}"
            )
        elif for_finish and check_targets:
            errors.extend(_local_link(project_root, target))

        delta = impact.delta.strip()
        delta_match = re.fullmatch(r"(requirements|design|data|api|version)\.md#(.+)", delta)
        if not delta_match:
            errors.append(
                f"{impact.impact_id} 的 Version delta 必须指向当前 version 文件锚点：{delta}"
            )
        else:
            delta_file = version_root / f"{delta_match.group(1)}.md"
            if not delta_file.is_file():
                errors.append(f"Impact delta 文件不存在：{delta_file}")
            else:
                errors.extend(_local_link(version_root, delta))

        verification = impact.verification.strip()
        if impact.state in {"verified", "synced"} and verification in {"", "—", "-"}:
            errors.append(f"{impact.impact_id} 已验证但缺少 Verification 证据")
        elif for_finish:
            link_errors = _local_link(version_root, verification)
            errors.extend(link_errors)
            if not link_errors:
                proof = (version_root / verification.split('#')[0]).read_text(encoding='utf-8')
                results = re.findall(r'(?m)^\|\s*V\d+-REQ-\d{3}-AC-\d{3}\s*\|[^\n]*?\|\s*(PASS|FAIL|BLOCKED)\s*\|', proof)
                if not results or any(result != 'PASS' for result in results):
                    errors.append(f'{impact.impact_id} 缺少全部 PASS 的影响验收证据')

    return errors, impacts


def _sync_states(version_text: str) -> dict[str, str]:
    states: dict[str, str] = {}
    for document in (*STEERING_FILES, 'current/product.md'):
        match = re.search(
            rf"(?m)^\|\s*`?{re.escape(document)}`?\s*\|\s*([^|]+?)\s*\|",
            version_text,
        )
        if match:
            states['product.md' if document == 'current/product.md' else document] = match.group(1).strip().strip("`")
    return states


def _version_errors(project_root: Path, row: VersionRow, *, candidate: bool = False) -> list[str]:
    errors: list[str] = []
    expected_path = f"docs/sdd/specs/{row.version}/"
    if row.path.rstrip("/") + "/" != expected_path:
        errors.append(
            f"{row.version} 路径必须为 {expected_path}，实际为 {row.path or '<empty>'}"
        )

    version_root = project_root / "docs/sdd/specs" / row.version
    version_file = version_root / "version.md"
    if not version_file.is_file():
        errors.append(f"{row.version} 缺少 version.md")
        return errors

    text = version_file.read_text(encoding="utf-8")
    actual_version = _metadata(text, "Version")
    actual_prefix = _metadata(text, "Version Prefix")
    actual_status = _metadata(text, "Status")
    expected_prefix = row.version.upper()

    if actual_version != row.version:
        errors.append(
            f"{row.version} 的 version.md Version 不一致：{actual_version or '<missing>'}"
        )
    if actual_prefix != expected_prefix:
        errors.append(
            f"{row.version} 的 Version Prefix 必须为 {expected_prefix}，实际为 {actual_prefix or '<missing>'}"
        )
    if actual_status != row.status:
        errors.append(
            f"{row.version} 的 version.md Status 与注册表不一致：{actual_status or '<missing>'} != {row.status}"
        )

    if row.status == 'draft':
        return errors
    errors.extend(_graph_errors(version_root, row.version))
    allowed_ids = set(_declarations(version_root))
    for dependency in re.findall(r'\bv[1-9][0-9]*\b', _section(text, 'Historical dependencies')):
        dependency_root = version_root.parent / dependency
        registry_rows, _ = _parse_registry(project_root / 'docs/sdd/versions.md')
        if not any(r.version == dependency and r.status == 'finished' for r in registry_rows):
            errors.append(f'历史依赖必须为已登记 finished version：{dependency}')
        else:
            allowed_ids.update(_declarations(dependency_root))
    wrong_ids: set[str] = set()
    wrong_impacts: set[str] = set()
    impact_references: set[str] = set()
    expected_id_prefix = f"{expected_prefix}-"
    for name in SCANNED_FILES:
        file_path = version_root / name
        if not file_path.is_file():
            continue
        file_text = file_path.read_text(encoding="utf-8")
        for identifier in ID_RE.findall(file_text):
            if identifier.isupper() and identifier not in allowed_ids:
                wrong_ids.add(identifier)
        for identifier in IMPACT_ID_RE.findall(file_text):
            impact_references.add(identifier)
            if not identifier.startswith(expected_id_prefix):
                wrong_impacts.add(identifier)
    if wrong_ids:
        errors.append(
            f"{row.version} 引用未声明或未授权的 ID：{', '.join(sorted(wrong_ids))}"
        )

    if wrong_impacts:
        errors.append(
            f"{row.version} 中 Impact ID 前缀必须为 {expected_prefix}-IMP-，发现：{', '.join(sorted(wrong_impacts))}"
        )

    if not (_section(text, 'Steering Impact Manifest') or _section(text, 'Baseline Impact Manifest')) and not (version_root / 'design.md').exists():
        return list(dict.fromkeys(errors))
    manifest_errors, impacts = _manifest_errors(project_root, row, text, candidate=candidate)
    errors.extend(manifest_errors)
    manifest_ids = {impact.impact_id for impact in impacts}
    for impact_id in sorted(impact_references - manifest_ids):
        errors.append(f"文档引用了未登记的 Manifest Impact：{impact_id}")

    return list(dict.fromkeys(errors))


def _finish_errors(project_root: Path, row: VersionRow, *, candidate: bool = False, check_targets: bool = True) -> list[str]:
    errors: list[str] = []
    version_root = project_root / "docs/sdd/specs" / row.version
    version_file = version_root / "version.md"
    if not version_file.is_file():
        return [f"{row.version} 缺少 version.md，无法检查 finished 门禁"]

    expected_status = 'active' if candidate else 'finished'
    if row.status != expected_status:
        errors.append(f"{row.version} 的注册表状态必须为 {expected_status}")

    version_text = version_file.read_text(encoding="utf-8")
    if "{{" in version_text:
        errors.append(f"{row.version}/version.md 仍有模板占位符")
    version_status = _metadata(version_text, "Status")
    version_finished = _metadata(version_text, "Finished")
    if version_status != expected_status:
        errors.append(f"{row.version} 的 version.md 状态必须为 {expected_status}")
    if candidate:
        if row.finished not in {'', '—', '-'} or version_finished not in {None, '', '—', '-'}:
            errors.append('收尾候选不得提前填写 Finished 日期')
    elif row.finished in {"", "—", "-"} or version_finished in {None, "", "—", "-"}:
        errors.append(f"{row.version} 缺少真实 Finished 日期")
    elif row.finished != version_finished:
        errors.append(
            f"{row.version} 的 Finished 日期不一致：注册表 {row.finished}，version.md {version_finished}"
        )

    for name in CORE_FILES:
        file_path = version_root / name
        if not file_path.is_file():
            errors.append(f"{row.version} finished 前缺少 {name}")
        elif not file_path.read_text(encoding='utf-8').strip() or "{{" in file_path.read_text(encoding="utf-8"):
            errors.append(f"{row.version}/{name} 仍有模板占位符")

    design_file = version_root / "design.md"
    if design_file.is_file():
        if not design_file.read_text(encoding='utf-8').strip() or "{{" in design_file.read_text(encoding="utf-8"):
            errors.append(f"{row.version}/design.md 仍有模板占位符")
    elif not re.search(
        r"(?im)^\s*-\s*(?:\*\*)?Design decision(?:\*\*)?\s*:\s*no new design\b",
        version_text,
    ) and 'no new design' not in _section(version_text, 'Design decision').lower():
        errors.append(
            f"{row.version} 缺少 design.md；若无需新增设计，必须在 version.md 记录 Design decision"
        )

    tasks_file = version_root / "tasks.md"
    if tasks_file.is_file():
        tasks_text = tasks_file.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*-\s*\[\s\]\s+\*\*V[1-9][0-9]*-TASK-", tasks_text):
            errors.append(f"{row.version} 仍有未关闭 TASK")

    if _metadata(_section(version_text, 'Alignment review'), 'Result') != 'PASS':
        errors.append(f"{row.version} 缺少 PASS 的 Alignment review")

    manifest_errors, impacts = _manifest_errors(
        project_root, row, version_text, for_finish=True, candidate=candidate, check_targets=check_targets
    )
    errors.extend(manifest_errors)

    sync_states = _sync_states(version_text)
    for document in STEERING_FILES:
        if document not in sync_states:
            errors.append(f"{row.version} Steering sync 缺少 {document}")
            continue
        state = sync_states[document]
        if state not in RESOLVED_SYNC:
            if state == "待确认":
                errors.append(f"{row.version} Steering sync 仍有待确认项：{document}")
            else:
                errors.append(f"{row.version} Steering sync 状态非法：{document}={state}")

    impacted_files = {
        MANIFEST_DOMAINS[impact.domain]
        for impact in impacts
        if impact.domain in MANIFEST_DOMAINS
    }
    if any(impact.domain == 'product' for impact in impacts):
        match = re.search(r'(?m)^\|\s*`?current/product\.md`?\s*\|\s*([^|]+)', version_text)
        sync_states['product.md'] = match.group(1).strip() if match else ''
    for document in impacted_files:
        if sync_states.get(document) != "已同步":
            errors.append(f"Manifest 指向 {document}，Steering sync 中 {document} 必须标记为 已同步")
    for document, state in sync_states.items():
        if state == "已同步" and document not in impacted_files:
            errors.append(f"{document} 标记为 已同步，但 Manifest 没有对应 Impact")

    if tasks_file.is_file():
        tasks_text = tasks_file.read_text(encoding="utf-8")
        task_impacts = set(IMPACT_ID_RE.findall(tasks_text))
        manifest_impacts = {impact.impact_id for impact in impacts}
        for impact_id in sorted(task_impacts - manifest_impacts):
            errors.append(f"TASK 引用了未登记的 Manifest Impact：{impact_id}")
        for impact_id in sorted(manifest_impacts - task_impacts):
            errors.append(f"Manifest Impact 未被任何 TASK 引用：{impact_id}")
        for impact in impacts:
            owners = [body for _, _, body in _task_blocks(tasks_text) if impact.impact_id in (_metadata(body, 'Steering impact') or '')]
            # Accept the old non-bold field during migration, but require evidence ownership.
            if not owners:
                owners = [body for _, _, body in _task_blocks(tasks_text) if impact.impact_id in body]
            if not any((_metadata(body, 'Evidence') or '').split('#')[0] == impact.verification.split('#')[0] and _metadata(body, 'Status') == 'done' for body in owners):
                errors.append(f'{impact.impact_id} Verification 必须来自负责且已通过的 TASK')

    if not _section(version_text, 'Completion evidence').strip():
        errors.append(f"{row.version} 缺少 Completion evidence")

    errors.extend(_graph_errors(version_root, row.version, finish=True))

    return errors


def validate_project(project_root: Path, finish_version: str | None = None, *, check_finish: str | None = None) -> list[str]:
    """Return deterministic SDD consistency errors; an empty list means valid."""

    project_root = Path(project_root).resolve()
    registry_path = project_root / "docs/sdd/versions.md"
    rows, errors = _parse_registry(registry_path)

    if registry_path.is_file():
        if not (project_root / "docs/AGENTS.md").is_file():
            errors.append("缺少项目 SDD 入口：docs/AGENTS.md")
        steering_root = project_root / "docs/sdd/steering"
        for name in STEERING_FILES[:3]:
            if not (steering_root / name).is_file():
                errors.append(f"缺少必需 Steering：docs/sdd/steering/{name}")

    seen: set[str] = set()
    for row in rows:
        if row.version in seen:
            errors.append(f"版本重复登记：{row.version}")
        seen.add(row.version)
        if not VERSION_RE.fullmatch(row.version):
            errors.append(f"version ID 非法：{row.version}，必须匹配 v[1-9][0-9]*")
        if row.status not in ALLOWED_STATUS:
            errors.append(f"{row.version} 状态非法：{row.status}")
        version_file = project_root / 'docs/sdd/specs' / row.version / 'version.md'
        if VERSION_RE.fullmatch(row.version) and version_file.is_file():
            metadata = version_file.read_text(encoding='utf-8')
            if row.status != 'draft' and (not _date(row.started) or _metadata(metadata, 'Started') != row.started):
                errors.append(f'{row.version} Started 日期非法或不一致')
            if row.status == 'finished' and (not _date(row.finished) or row.finished < row.started):
                errors.append(f'{row.version} Finished 日期非法或早于 Started')
            if row.status != 'finished' and (row.finished not in {'', '—', '-'} or _metadata(metadata, 'Finished') not in {None, '', '—', '-'}):
                errors.append(f'{row.version} 未完成时不得填写 Finished 日期')

    specs = project_root / 'docs/sdd/specs'
    if specs.is_dir():
        for directory in specs.iterdir():
            if directory.is_dir() and VERSION_RE.fullmatch(directory.name) and directory.name not in seen:
                errors.append(f'未登记的 version 目录：{directory.name}')

    active = [row.version for row in rows if row.status == "active"]
    if len(active) > 1:
        errors.append(f"同时存在多个 active version：{', '.join(active)}")

    valid_rows = sorted((row for row in rows if row.number > 0), key=lambda row: row.number)
    for index, row in enumerate(valid_rows):
        if index < len(valid_rows) - 1 and row.status != "finished":
            later = valid_rows[index + 1].version
            errors.append(f"前一 version 未 finished：{row.version} 后仍登记 {later}")

    for row in rows:
        if VERSION_RE.fullmatch(row.version):
            errors.extend(_version_errors(project_root, row, candidate=row.version == check_finish))
            if row.status == 'finished':
                errors.extend(_finish_errors(project_root, row, check_targets=row.version == finish_version))

    selected = check_finish or finish_version
    if selected is not None:
        target = next((row for row in rows if row.version == selected), None)
        if target is None:
            errors.append(f"指定的 version 未登记：{selected}")
        else:
            errors.extend(_finish_errors(project_root, target, candidate=check_finish is not None))

    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate versioned HNS-SDD documents")
    parser.add_argument("project", type=Path, help="Project root containing docs/sdd")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--finish", dest="finish_version", help="Validate an already finished vN including current targets")
    mode.add_argument("--check-finish", help="Read-only check of an active closing candidate with synced baselines")
    args = parser.parse_args(argv)

    try:
        errors = validate_project(args.project, finish_version=args.finish_version, check_finish=args.check_finish)
    except (OSError, UnicodeError) as exc:
        errors = [f'无法读取 SDD 文档：{exc}']
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("SDD validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
