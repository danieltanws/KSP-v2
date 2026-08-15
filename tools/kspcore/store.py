"""Reading the KSP stores off disk.

Two stores, both plain CSV so the user can edit them in a spreadsheet:

    LAB  (ksp/lab)   documents, keyed by filename. No stable ID - PRD 5.1.
    LEAD (ksp/lead)  actors and authorship, keyed by an auto-number ID.

Multi-select fields are semicolon-separated inside one cell (PRD 4), e.g.
``Indonesia;Southeast Asia``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

MULTI_SEP = ";"

#: Rows carrying this record type are excluded from every agent query.
#: A folder row has every field blank, and blank rows read as real entries.
FOLDER = "Folder"
DOCUMENT = "Document"


def repo_root() -> Path:
    """The project root, found relative to this file."""
    return Path(__file__).resolve().parents[2]


def split_multi(cell: str | None) -> list[str]:
    """Split a semicolon-separated multi-select cell into clean values."""
    if not cell:
        return []
    return [part.strip() for part in cell.split(MULTI_SEP) if part.strip()]


def read_csv(path: Path) -> list[dict]:
    """Read a UTF-8 CSV with a header row. Missing file reads as empty."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(handle)
        ]


def role_for(position: str | int) -> str:
    """Derive authorship role from position: 1 -> Primary, else Co.

    PRD 5.3 specifies role as a formula over position, not a stored column.
    Deriving it here is the CSV equivalent - changing the rule means editing
    this function, not re-entering every row.
    """
    try:
        return "Primary" if int(position) == 1 else "Co"
    except (TypeError, ValueError):
        return "Co"


@dataclass
class Store:
    """The loaded contents of ksp/, with folder rows kept but flagged."""

    root: Path
    sources: list[dict]
    actors: list[dict]
    authorship: list[dict]

    @classmethod
    def load(cls, root: Path | str | None = None) -> "Store":
        base = Path(root) if root else repo_root() / "ksp"
        return cls(
            root=base,
            sources=read_csv(base / "lab" / "sources.csv"),
            actors=read_csv(base / "lead" / "actors.csv"),
            authorship=read_csv(base / "lead" / "authorship.csv"),
        )

    # -- LAB ---------------------------------------------------------------

    @property
    def documents_dir(self) -> Path:
        return self.root / "lab" / "documents"

    def documents(self) -> list[dict]:
        """Source rows that are documents. Folder rows are never returned."""
        return [r for r in self.sources if r.get("record_type") != FOLDER]

    def folders(self) -> list[dict]:
        return [r for r in self.sources if r.get("record_type") == FOLDER]

    def source_by_file(self, filename: str) -> dict | None:
        for row in self.documents():
            if row.get("file") == filename:
                return row
        return None

    # -- LEAD --------------------------------------------------------------

    def actor_by_id(self, actor_id: str) -> dict | None:
        for row in self.actors:
            if row.get("id") == str(actor_id).strip():
                return row
        return None

    def authors_of(self, filename: str) -> list[dict]:
        """Authorship rows for one document, ordered by position, role derived."""
        rows = [r for r in self.authorship if r.get("source_file") == filename]

        def sort_key(row):
            try:
                return int(row.get("position") or 0)
            except ValueError:
                return 0

        out = []
        for row in sorted(rows, key=sort_key):
            actor = self.actor_by_id(row.get("actor_id", ""))
            out.append(
                {
                    **row,
                    "role": role_for(row.get("position", "")),
                    "actor_name": actor.get("name") if actor else "(unknown actor)",
                }
            )
        return out
