"""The integrity check. Required on every agent start (PRD 4).

LAB rows are joined to files by a string match and nothing else. Rename a
file on disk and the link breaks silently - the row stays, the agent believes
in it, and the document behind it can never be opened.

Without this check that failure surfaces as *thin evidence* rather than as an
error, which is the silence problem in a new place. So it runs first, before
any question is answered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .store import Store

#: Files in lab/documents/ that are not documents.
IGNORED_FILES = {".gitkeep", ".DS_Store"}


@dataclass
class IntegrityReport:
    matched: list[str] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)  # (file, row name)
    unfiled: list[str] = field(default_factory=list)
    folder_rows: int = 0
    rows_without_file: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when nothing is broken. Unfiled files are a warning, not a break."""
        return not self.missing and not self.rows_without_file

    def render(self) -> str:
        lines = ["INTEGRITY CHECK"]
        lines.append(f"  ✓ {_plural(len(self.matched), 'row')} matched to files")

        if self.missing:
            if len(self.missing) == 1:
                lines.append("  ✗ 1 row references a missing file:")
            else:
                lines.append(f"  ✗ {len(self.missing)} rows reference missing files:")
            width = max(len(f) for f, _ in self.missing)
            for filename, row_name in self.missing:
                lines.append(f"      - {filename.ljust(width)}  (row: {row_name})")
        else:
            lines.append("  ✓ no rows reference missing files")

        if self.rows_without_file:
            lines.append(f"  ✗ {_plural(len(self.rows_without_file), 'document row')} with no file value:")
            for row_name in self.rows_without_file:
                lines.append(f"      - {row_name}")

        if self.unfiled:
            lines.append(f"  ⚠ {_plural(len(self.unfiled), 'file')} present but unfiled:")
            for filename in self.unfiled:
                lines.append(f"      - {filename}")
        else:
            lines.append("  ✓ no files present but unfiled")

        if self.folder_rows:
            lines.append(f"  · {_plural(self.folder_rows, 'folder row')} excluded from queries")

        return "\n".join(lines)


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def check(store: Store) -> IntegrityReport:
    report = IntegrityReport(folder_rows=len(store.folders()))

    filed: set[str] = set()
    for row in store.documents():
        filename = row.get("file", "")
        row_name = row.get("name") or "(unnamed row)"
        if not filename:
            report.rows_without_file.append(row_name)
            continue
        filed.add(filename)
        if (store.documents_dir / filename).is_file():
            report.matched.append(filename)
        else:
            report.missing.append((filename, row_name))

    if store.documents_dir.is_dir():
        for path in sorted(store.documents_dir.iterdir()):
            if path.is_file() and path.name not in IGNORED_FILES and path.name not in filed:
                report.unfiled.append(path.name)

    return report
