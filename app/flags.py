"""Transparent anomaly flags for RUP packages.

A flag is a question, not a verdict. Every flag carries its rule and its
threshold in plain language, so a citizen, journalist, or official can
recompute it from the same row. No flag uses the words corrupt, illegal,
or dark procurement as a conclusion.
"""
import re
from collections import Counter, defaultdict

PAGU_BESAR_THRESHOLD = 1_000_000_000
NILAI_BULAT_MIN = 100_000_000


def _normalize_name(name: str) -> str:
    text = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    words = [w for w in text.split() if len(w) > 2]
    return " ".join(words[:4])


def compute_flags(packages: list[dict]) -> dict[str, list[dict]]:
    """Return flags keyed by kode_rup."""
    flags: dict[str, list[dict]] = defaultdict(list)

    # Repeated similar packages from the same satker.
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for pkg in packages:
        key = (pkg["nama_satuan_kerja"], _normalize_name(pkg["nama_paket"]))
        groups[key].append(pkg)
    for members in groups.values():
        if len(members) >= 3:
            for pkg in members:
                flags[pkg["kode_rup"]].append({
                    "kode": "paket_serupa_berulang",
                    "judul": "Paket serupa berulang di satker yang sama",
                    "penjelasan": (
                        f"Satker ini punya {len(members)} paket dengan nama yang "
                        "sangat mirip. Perlu dicek apakah ini tahapan yang sah, "
                        "atau pemecahan paket yang patut dipertanyakan."
                    ),
                    "ambang": "Minimal 3 paket dengan 4 kata awal nama yang sama di satker yang sama",
                })

    for pkg in packages:
        total = pkg["total_nilai"]
        if total >= PAGU_BESAR_THRESHOLD:
            flags[pkg["kode_rup"]].append({
                "kode": "pagu_besar",
                "judul": "Pagu besar",
                "penjelasan": (
                    f"Total nilai Rp {total:,} mencapai atau melewati ambang "
                    "Rp 1.000.000.000. Paket besar wajar ada, tapi layak "
                    "diprioritaskan untuk dicek dokumen dan hasilnya."
                ),
                "ambang": "Total nilai >= Rp 1.000.000.000",
            })
        if total >= NILAI_BULAT_MIN and total % 10_000_000 == 0:
            flags[pkg["kode_rup"]].append({
                "kode": "nilai_bulat",
                "judul": "Nilai bulat besar",
                "penjelasan": (
                    "Total nilai adalah kelipatan Rp 10.000.000 dan cukup besar. "
                    "Angka bulat bisa jadi pembulatan perencanaan yang sah, "
                    "bisa juga tanda perkiraan yang tidak dirinci."
                ),
                "ambang": "Total nilai >= Rp 100.000.000 dan kelipatan Rp 10.000.000",
            })
        if pkg["metode_pengadaan"].lower() == "penunjukan langsung" and total >= 200_000_000:
            flags[pkg["kode_rup"]].append({
                "kode": "penunjukan_langsung_besar",
                "judul": "Penunjukan langsung dengan nilai besar",
                "penjelasan": (
                    "Metode penunjukan langsung dipakai untuk nilai yang cukup "
                    "besar. Perlu dicek dasar penunjukan dan dokumen pendukungnya, "
                    "karena metode ini tidak melalui kompetisi terbuka."
                ),
                "ambang": "Metode Penunjukan Langsung dan total nilai >= Rp 200.000.000",
            })
    return dict(flags)


def attach_flags(packages: list[dict]) -> list[dict]:
    flags = compute_flags(packages)
    out = []
    for pkg in packages:
        item = dict(pkg)
        item["flags"] = flags.get(pkg["kode_rup"], [])
        item["jumlah_flag"] = len(item["flags"])
        out.append(item)
    return out


def summarize(packages: list[dict]) -> dict:
    flagged = attach_flags(packages)
    total = sum(p["total_nilai"] for p in flagged)
    per_metode: dict[str, dict] = {}
    for pkg in flagged:
        entry = per_metode.setdefault(pkg["metode_pengadaan"], {"jumlah": 0, "total_nilai": 0})
        entry["jumlah"] += 1
        entry["total_nilai"] += pkg["total_nilai"]
    per_provinsi: dict[str, dict] = {}
    for pkg in flagged:
        entry = per_provinsi.setdefault(pkg["provinsi"], {"jumlah": 0, "total_nilai": 0})
        entry["jumlah"] += 1
        entry["total_nilai"] += pkg["total_nilai"]
    flag_counts = Counter()
    for pkg in flagged:
        for flag in pkg["flags"]:
            flag_counts[flag["kode"]] += 1
    return {
        "jumlah_paket": len(flagged),
        "total_nilai": total,
        "rata_rata_nilai": round(total / len(flagged)) if flagged else 0,
        "jumlah_berbendera": sum(1 for p in flagged if p["flags"]),
        "per_metode": per_metode,
        "per_provinsi": per_provinsi,
        "per_flag": dict(flag_counts),
    }
