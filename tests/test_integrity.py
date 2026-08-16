"""The integrity check must surface a broken link as an error, never as thin evidence."""

from __future__ import annotations

from conftest import SOURCE_HEADER, write_rows
from kspcore import integrity
from kspcore.store import Store


def test_clean_store_reports_ok(demo):
    report = integrity.check(demo)
    assert report.ok
    assert len(report.matched) == len(demo.documents())
    assert report.missing == []
    assert report.unfiled == []


def test_folder_rows_are_excluded_from_the_file_check(demo):
    report = integrity.check(demo)
    assert report.folder_rows == 1
    # The folder row has no file and must not be counted as a broken link.
    assert report.rows_without_file == []


def test_renamed_file_is_reported_as_missing(scratch):
    target = scratch / "lab" / "documents" / "Heat_PM25_Study.pdf"
    target.rename(target.with_name("Heat_PM25_Study_v2.pdf"))

    report = integrity.check(Store.load(scratch))

    assert not report.ok
    assert ("Heat_PM25_Study.pdf", "Heat and PM2.5 compound exposure study") in report.missing
    assert report.unfiled == ["Heat_PM25_Study_v2.pdf"]


def test_unfiled_file_is_a_warning_not_an_error(scratch):
    (scratch / "lab" / "documents" / "Indus_Valley_Report.pdf").write_text("x", encoding="utf-8")

    report = integrity.check(Store.load(scratch))

    assert report.unfiled == ["Indus_Valley_Report.pdf"]
    assert report.ok, "an unfiled document is a warning - it breaks no existing reference"


def test_gitkeep_is_not_reported_as_unfiled(empty):
    assert integrity.check(empty).unfiled == []


def test_render_matches_the_specified_format(scratch):
    store = Store.load(scratch)
    remaining = len(store.documents()) - 1
    (scratch / "lab" / "documents" / "Heat_PM25_Study.pdf").unlink()
    (scratch / "lab" / "documents" / "Stray.pdf").write_text("x", encoding="utf-8")

    text = integrity.check(Store.load(scratch)).render()

    assert text.startswith("INTEGRITY CHECK\n")
    assert f"  ✓ {remaining} rows matched to files" in text
    assert "  ✗ 1 row references a missing file:" in text
    assert "Heat_PM25_Study.pdf" in text
    assert "(row: Heat and PM2.5 compound exposure study)" in text
    assert "  ⚠ 1 file present but unfiled:" in text
    assert "      - Stray.pdf" in text


def test_clean_run_states_both_checks_ran(demo):
    text = integrity.check(demo).render()
    # Silence would be indistinguishable from the check not running.
    assert "no rows reference missing files" in text
    assert "no files present but unfiled" in text


def test_document_row_with_no_file_is_an_error(scratch):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["Orphan row", "", "Document", "d", "", "PLANET", "Urban Liveability",
          "Pollution", "Indonesia;Southeast Asia", "Research", "Someone", "",
          "2024", "", "2026-08-14"]],
    )

    report = integrity.check(Store.load(scratch))

    assert report.rows_without_file == ["Orphan row"]
    assert not report.ok


def test_plural_agreement_in_the_missing_line(scratch):
    docs = scratch / "lab" / "documents"
    (docs / "Heat_PM25_Study.pdf").unlink()
    single = integrity.check(Store.load(scratch)).render()
    assert "1 row references a missing file:" in single

    (docs / "Jakarta_Air_Quality_Review.pdf").unlink()
    plural = integrity.check(Store.load(scratch)).render()
    assert "2 rows reference missing files:" in plural
