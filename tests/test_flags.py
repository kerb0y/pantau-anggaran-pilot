import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.flags import attach_flags, summarize
from app.loader import default_sample_path, load_csv


def sample():
    return load_csv(default_sample_path())


def test_loader_reads_all_rows():
    rows = sample()
    assert len(rows) == 24
    assert rows[0]["kode_rup"] == "67179486"
    assert rows[0]["total_nilai"] == 109890000


def test_pagu_besar_flag():
    flagged = attach_flags(sample())
    big = [p for p in flagged if p["total_nilai"] >= 1_000_000_000]
    assert big
    assert all(any(f["kode"] == "pagu_besar" for f in p["flags"]) for p in big)


def test_repeated_similar_packages_flag():
    flagged = attach_flags(sample())
    repeated = [p for p in flagged if any(f["kode"] == "paket_serupa_berulang" for f in p["flags"])]
    assert len(repeated) >= 3


def test_summary_totals_match_rows():
    rows = sample()
    s = summarize(rows)
    assert s["jumlah_paket"] == len(rows)
    assert s["total_nilai"] == sum(r["total_nilai"] for r in rows)
    assert s["jumlah_berbendera"] > 0
    assert "Jawa Timur" in s["per_provinsi"]


def test_flags_are_questions_not_verdicts():
    flagged = attach_flags(sample())
    for pkg in flagged:
        for flag in pkg["flags"]:
            assert "korupsi" not in flag["judul"].lower()
            assert "ambang" in flag
