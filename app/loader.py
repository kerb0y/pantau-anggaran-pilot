"""Load RUP CSV exports in the data.inaproc.id Anggaran format.

The loader accepts the 13 Anggaran columns plus optional provinsi and
kabupaten_kota columns added for the pilot map. It never invents a
location: rows without province are grouped under "Lokasi belum tersedia"
and are excluded from the map, not plotted at a guessed coordinate.
"""
import csv
import re
from pathlib import Path

REQUIRED = [
    "nama_instansi", "nama_satuan_kerja", "tahun_anggaran",
    "cara_pengadaan", "metode_pengadaan", "jenis_pengadaan",
    "nama_paket", "kode_rup", "sumber_dana",
    "produk_dalam_negeri", "umk", "total_nilai",
]


def parse_amount(value) -> int:
    if value is None:
        return 0
    text = str(value).strip().replace("Rp", "").replace(".", "").replace(",", "")
    text = re.sub(r"[^0-9-]", "", text)
    try:
        return int(text) if text else 0
    except ValueError:
        return 0


def load_csv(path: str | Path) -> list[dict]:
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        missing = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Kolom wajib hilang: {', '.join(missing)}")
        rows: list[dict] = []
        for raw in reader:
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in raw.items()}
            row["total_nilai"] = parse_amount(row.get("total_nilai"))
            try:
                row["tahun_anggaran"] = int(row.get("tahun_anggaran") or 0)
            except ValueError:
                row["tahun_anggaran"] = 0
            row["provinsi"] = (row.get("provinsi") or "Lokasi belum tersedia").strip()
            row["kabupaten_kota"] = (row.get("kabupaten_kota") or "").strip()
            rows.append(row)
        return rows


def default_sample_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample_kemenkes_2026.csv"
