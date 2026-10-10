"""Regenerate STATUS.md and docs/qa/traceability.md from the project's tracking files.

Inputs: spec front matter + tasks.md checklists (specs/), requirements and roadmap
(docs/product/), Q&A log and test cases (docs/qa/), CHANGELOG.md.

Usage:
    python scripts/status.py          # rewrite STATUS.md and docs/qa/traceability.md
    python scripts/status.py --check  # exit 1 if either file is out of date

Stdlib only, so it runs with any Python 3.10+ (no venv needed).
Everything between the NOTES markers in STATUS.md is hand-written and preserved.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.md"
SPECS = ROOT / "specs"
REQUIREMENTS = ROOT / "docs" / "product" / "requirements.md"
ROADMAP = ROOT / "docs" / "product" / "roadmap.md"
CHANGELOG = ROOT / "CHANGELOG.md"
QA = ROOT / "docs" / "qa"
QUESTIONS = QA / "questions.md"
TEST_CASES = QA / "test-cases"
TRACEABILITY = QA / "traceability.md"

NOTES_START = "<!-- NOTES:START (hand-written, kept by scripts/status.py) -->"
NOTES_END = "<!-- NOTES:END -->"
DEFAULT_NOTES = "- (none)"

REQ_RE = re.compile(r"REQ-[A-Z]+-\d{3}")
RESULT_KINDS = ("pass", "fail", "blocked", "not run")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ---------------------------------------------------------------- specs and tasks


def front_matter(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = re.sub(r"\s+#.*$", "", value).strip()  # drop trailing comments
        out[key.strip()] = value
    return out


def task_counts(text: str) -> tuple[int, int]:
    done = len(re.findall(r"^\s*- \[[xX]\]", text, re.M))
    open_ = len(re.findall(r"^\s*- \[ \]", text, re.M))
    return done, done + open_


def load_specs() -> list[dict[str, str]]:
    specs = []
    for spec_file in sorted(SPECS.glob("[0-9][0-9][0-9]-*/spec.md")):
        fm = front_matter(read(spec_file))
        done, total = task_counts(read(spec_file.parent / "tasks.md"))
        fm["tasks"] = f"{done}/{total}" if total else "—"
        fm["folder"] = spec_file.parent.name
        specs.append(fm)
    return specs


def roadmap_rows() -> list[tuple[str, str, str]]:
    rows = []
    for m in re.finditer(r"^\| (\d{3}) \| ([^|]+?) \|.*?\| ([^|]*?) \|\s*$", read(ROADMAP), re.M):
        rows.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return rows


# ---------------------------------------------------------------- requirements


@dataclass
class Requirement:
    id: str
    status: str
    spec: str


def load_requirements() -> list[Requirement]:
    reqs = []
    for m in re.finditer(r"^\| (REQ-[A-Z]+-\d{3}) \|(.*)$", read(REQUIREMENTS), re.M):
        cells = [c.strip() for c in m.group(2).split("|")]
        # columns after ID: requirement, acceptance, status, spec, notes
        status = cells[2] if len(cells) > 2 else "?"
        spec = cells[3] if len(cells) > 3 else ""
        reqs.append(Requirement(m.group(1), status, spec))
    return reqs


# ---------------------------------------------------------------- QA


@dataclass
class TestCase:
    id: str
    spec: str
    title: str
    covers: list[str]
    modules: list[str]
    kind: str
    result: str  # one of RESULT_KINDS
    raw_result: str


@dataclass
class Question:
    id: str
    title: str
    status: str
    reqs: list[str] = field(default_factory=list)
    specs: list[str] = field(default_factory=list)


def classify(result: str) -> str:
    low = result.lower()
    return next((k for k in RESULT_KINDS if low.startswith(k)), "not run")


def load_test_cases() -> list[TestCase]:
    cases = []
    for path in sorted(TEST_CASES.glob("*.md")):
        for m in re.finditer(r"^\| (TC-(\d{3})-\d{2}) \|(.*)$", read(path), re.M):
            cells = [c.strip() for c in m.group(3).split("|")]
            if len(cells) < 6:
                continue
            title, covers, modules, kind, _test, result = cells[:6]
            cases.append(
                TestCase(
                    id=m.group(1),
                    spec=m.group(2),
                    title=title,
                    covers=REQ_RE.findall(covers) + re.findall(r"AC-\d+", covers),
                    modules=[x.strip() for x in modules.split(",") if x.strip()],
                    kind=kind,
                    result=classify(result),
                    raw_result=result,
                )
            )
    return cases


def load_questions() -> list[Question]:
    questions = []
    parts = re.split(r"^### (Q-\d{3}) — (.+)$", read(QUESTIONS), flags=re.M)
    # parts = [preamble, id, title, body, id, title, body, ...]
    for i in range(1, len(parts) - 2, 3):
        qid, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        status_m = re.search(r"\*\*Status:\*\*\s*([\w-]+)", body)
        context_m = re.search(r"\*\*Context:\*\*(.*)", body)
        context = context_m.group(1) if context_m else ""
        questions.append(
            Question(
                id=qid,
                title=title,
                status=status_m.group(1) if status_m else "?",
                reqs=REQ_RE.findall(context),
                specs=re.findall(r"spec \[?(\d{3})", context),
            )
        )
    return questions


def tc_summary(cases: list[TestCase]) -> str:
    if not cases:
        return "—"
    c = Counter(tc.result for tc in cases)
    extra = ", ".join(f"{c[k]} {k}" for k in ("fail", "blocked", "not run") if c[k])
    return f"{c['pass']}/{len(cases)} pass" + (f" ({extra})" if extra else "")


# ---------------------------------------------------------------- CHANGELOG / notes


def changelog_info() -> tuple[str, int]:
    text = read(CHANGELOG)
    released = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, re.M)
    version = released[0] if released else "unreleased"
    unreleased = re.search(r"^## \[Unreleased\]\s*\n(.*?)(?=^## \[|\Z)", text, re.M | re.S)
    pending = len(re.findall(r"^- ", unreleased.group(1), re.M)) if unreleased else 0
    return version, pending


def existing_notes() -> str:
    m = re.search(re.escape(NOTES_START) + r"\n(.*?)\n" + re.escape(NOTES_END), read(STATUS), re.S)
    return m.group(1).strip() if m and m.group(1).strip() else DEFAULT_NOTES


# ---------------------------------------------------------------- renderers


def render_status() -> str:
    specs = load_specs()
    by_id = {s.get("id", ""): s for s in specs}
    version, pending = changelog_info()
    reqs = load_requirements()
    cases = load_test_cases()
    questions = load_questions()
    cases_by_spec: dict[str, list[TestCase]] = defaultdict(list)
    for tc in cases:
        cases_by_spec[tc.spec].append(tc)

    active = next(
        (s for st in ("in-progress", "approved", "draft") for s in specs if s.get("status") == st),
        None,
    )
    active_line = (
        f"[{active['id']} — {active.get('title', '')}](specs/{active['folder']}/spec.md) "
        f"· status **{active.get('status')}** · tasks {active['tasks']} "
        f"· tests {tc_summary(cases_by_spec.get(active['id'], []))}"
        if active
        else "none"
    )
    open_qs = [q for q in questions if q.status == "open"]

    lines = [
        "# Project Status",
        "",
        "> Generated by `python scripts/status.py` from spec front matter, `tasks.md` checklists,",
        "> `docs/product/requirements.md`, the roadmap, `docs/qa/` and `CHANGELOG.md`.",
        "> Do not edit by hand, except inside the Notes section at the bottom.",
        "",
        f"- **Released version:** {version}"
        + (f" · {pending} unreleased change(s) in CHANGELOG" if pending else ""),
        "- **Milestone:** MVP",
        f"- **Active spec:** {active_line}",
        f"- **Open questions:** {len(open_qs)} (see below)",
        "",
        "## Features",
        "",
        "| Spec | Title | Status | Version | Tasks | Tests | Target | Updated |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def spec_row(spec_id: str, s: dict[str, str], title: str, target: str) -> str:
        return (
            f"| [{spec_id}](specs/{s['folder']}/spec.md) | {s.get('title', title)} "
            f"| {s.get('status', '?')} | {s.get('version', '?')} | {s['tasks']} "
            f"| {tc_summary(cases_by_spec.get(spec_id, []))} "
            f"| {s.get('target_release', target)} | {s.get('updated', '')} |"
        )

    seen = set()
    for spec_id, title, target in roadmap_rows():
        seen.add(spec_id)
        s = by_id.get(spec_id)
        if s:
            lines.append(spec_row(spec_id, s, title, target))
        else:
            lines.append(f"| {spec_id} | {title} | not started | — | — | — | {target} | — |")
    for s in specs:  # specs not listed in the roadmap
        if s.get("id") not in seen:
            lines.append(spec_row(s.get("id", "?"), s, "", ""))

    req_counts = Counter(r.status for r in reqs)
    summary = ", ".join(
        f"{req_counts[k]} {k}"
        for k in ["done", "in-progress", "changed", "planned", "dropped"]
        if req_counts[k]
    )
    in_flight = [f"{r.id} ({r.status})" for r in reqs if r.status in ("in-progress", "changed")]
    lines += [
        "",
        "## Requirements",
        "",
        f"{len(reqs)} total: {summary}." if reqs else "No requirements found.",
    ]
    if in_flight:
        lines.append(f"In flight: {', '.join(in_flight)}.")

    failing = [tc for tc in cases if tc.result == "fail"]
    lines += [
        "",
        "## Quality",
        "",
        f"Test cases: {tc_summary(cases)}. Details per spec in `docs/qa/test-cases/`;"
        " REQ → test → module map in [docs/qa/traceability.md](docs/qa/traceability.md).",
    ]
    if failing:
        lines.append("")
        lines.append("Failing:")
        lines += [f"- {tc.id} {tc.title}: {tc.raw_result}" for tc in failing]
    lines += ["", "### Open questions ([docs/qa/questions.md](docs/qa/questions.md))", ""]
    if open_qs:
        for q in open_qs:
            where = ", ".join([f"spec {s}" for s in q.specs] + q.reqs) or "process"
            lines.append(f"- **{q.id}** {q.title} ({where})")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Notes and blockers",
        "",
        NOTES_START,
        existing_notes(),
        NOTES_END,
        "",
    ]
    return "\n".join(lines)


def render_traceability() -> str:
    reqs = load_requirements()
    cases = load_test_cases()
    questions = load_questions()
    spec_folders = {s.get("id", ""): s["folder"] for s in load_specs()}

    lines = [
        "# Traceability matrix",
        "",
        "> Generated by `python scripts/status.py`. Do not edit by hand.",
        "> Requirement → spec → test cases (last result) → modules → open questions.",
        "",
        "| Requirement | Status | Spec | Test cases | Modules | Open questions |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in reqs:
        tcs = [tc for tc in cases if r.id in tc.covers]
        spec = r.spec
        if spec in spec_folders:
            spec = f"[{spec}](../../specs/{spec_folders[spec]}/spec.md)"
        tc_text = ", ".join(f"{tc.id} ({tc.result})" for tc in tcs) or "—"
        modules = sorted({m for tc in tcs for m in tc.modules})
        mod_text = ", ".join(f"`{m}`" for m in modules) or "—"
        qs = [q.id for q in questions if q.status == "open" and r.id in q.reqs]
        lines.append(
            f"| {r.id} | {r.status} | {spec or '—'} | {tc_text} | {mod_text} | {', '.join(qs) or '—'} |"
        )

    by_module: dict[str, list[TestCase]] = defaultdict(list)
    for tc in cases:
        for m in tc.modules:
            by_module[m].append(tc)
    lines += [
        "",
        "## By module",
        "",
        "| Module | Test cases | Requirements |",
        "| --- | --- | --- |",
    ]
    for m in sorted(by_module):
        tcs = by_module[m]
        req_ids = sorted({c for tc in tcs for c in tc.covers if c.startswith("REQ-")})
        lines.append(
            f"| `{m}` | {', '.join(f'{tc.id} ({tc.result})' for tc in tcs)} "
            f"| {', '.join(req_ids) or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    outputs = {STATUS: render_status(), TRACEABILITY: render_traceability()}
    if "--check" in sys.argv:
        stale = [p for p, text in outputs.items() if read(p) != text]
        if stale:
            names = ", ".join(str(p.relative_to(ROOT)) for p in stale)
            print(f"Out of date: {names}. Run: python scripts/status.py")
            return 1
        print("STATUS.md and docs/qa/traceability.md are up to date.")
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
