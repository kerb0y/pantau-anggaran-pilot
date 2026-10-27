"""Pantau Anggaran pilot, FastAPI application.

Run locally:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/ for the dashboard and
http://127.0.0.1:8000/docs for the API docs.

Data source for the pilot: data/sample_kemenkes_2026.csv in the
data.inaproc.id Anggaran format, plus provinsi and kabupaten_kota
columns added for the map. To use a real export, replace that file
with the CSV downloaded from data.inaproc.id/rup for one institution
and keep the same Anggaran column names. Set PANTAU_CSV_PATH to point
at a different file.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .flags import attach_flags, summarize
from .loader import default_sample_path, load_csv

PROVINCE_COORDS: dict[str, tuple[float, float]] = {
    "DKI Jakarta": (-6.2088, 106.8456),
    "Jawa Barat": (-6.9175, 107.6191),
    "Jawa Tengah": (-7.1509, 110.1403),
    "DI Yogyakarta": (-7.7956, 110.3695),
    "Jawa Timur": (-7.2575, 112.7521),
    "Banten": (-6.4058, 106.0640),
}

app = FastAPI(
    title="Pantau Anggaran Pilot",
    description=(
        "Dashboard pengawasan pengadaan untuk masyarakat. Data pilot "
        "berasal dari format RUP data.inaproc.id, bendera anomali "
        "bersifat pertanyaan yang bisa dicek ulang, bukan vonis."
    ),
    version="0.1.0",
)

FRONTEND = Path(__file__).resolve().parents[1] / "frontend" / "index.html"


def get_packages() -> list[dict]:
    csv_path = os.environ.get("PANTAU_CSV_PATH") or str(default_sample_path())
    return attach_flags(load_csv(csv_path))


@app.get("/")
def root():
    return FileResponse(FRONTEND)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "dataset": "pilot, satu instansi, format RUP Anggaran"}


@app.get("/api/summary")
def summary() -> dict:
    packages = get_packages()
    result = summarize(packages)
    result["catatan"] = (
        "Bendera anomali adalah pertanyaan untuk dicek, bukan bukti "
        "pelanggaran. Selalu periksa dokumen asli di SIRUP atau SPSE."
    )
    return result


@app.get("/api/packages")
def packages(
    q: str | None = None,
    metode: str | None = None,
    provinsi: str | None = None,
    hanya_berbendera: bool = False,
) -> dict:
    items = get_packages()
    if q:
        lowered = q.lower()
        items = [p for p in items if lowered in p["nama_paket"].lower() or lowered in p["nama_satuan_kerja"].lower()]
    if metode:
        items = [p for p in items if p["metode_pengadaan"].lower() == metode.lower()]
    if provinsi:
        items = [p for p in items if p["provinsi"].lower() == provinsi.lower()]
    if hanya_berbendera:
        items = [p for p in items if p["flags"]]
    items = sorted(items, key=lambda p: p["total_nilai"], reverse=True)
    return {"packages": items, "count": len(items)}


@app.get("/api/map")
def map_data() -> dict:
    packages = get_packages()
    summary_by_province = summarize(packages)["per_provinsi"]
    points = []
    for province, data in summary_by_province.items():
        if province in PROVINCE_COORDS:
            lat, lon = PROVINCE_COORDS[province]
            points.append({
                "provinsi": province,
                "latitude": lat,
                "longitude": lon,
                "jumlah_paket": data["jumlah"],
                "total_nilai": data["total_nilai"],
            })
    return {"points": points}
