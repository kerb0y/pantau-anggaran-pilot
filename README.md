# Pantau Anggaran Pilot

Dashboard pengawasan pengadaan pemerintah untuk masyarakat. Pilot ini dimulai dari satu instansi, Kementerian Kesehatan tahun 2026, memakai format tabel Anggaran dari data.inaproc.id, dan menampilkan pencarian paket, peta agregat per provinsi, serta bendera anomali yang transparan.

Prinsip utama project ini: bendera adalah pertanyaan untuk dicek, bukan vonis. Tidak ada paket yang dilabeli korupsi, ilegal, atau pengadaan gelap hanya karena terkena bendera. Setiap bendera menampilkan aturan dan ambangnya, supaya siapa pun bisa menghitung ulang dari baris data yang sama dan memeriksa dokumen asli di SIRUP atau SPSE.

## Status Data Pilot, Dibaca Dulu

File `data/sample_kemenkes_2026.csv` adalah DATA CONTOH PILOT, bukan dataset Kementerian Kesehatan penuh. Dataset penuh yang teramati di halaman data.inaproc.id untuk Kementerian Kesehatan 2026 adalah 23.960 paket dengan total Rp 50.964.906.049.663, dan file contoh ini hanya 24 baris untuk mendemokan fitur. Dua baris pertama meniru contoh baris yang teramati di halaman tersebut, yaitu perbaikan ventilator Rp 109.890.000 dan pengadaan audio set Rp 11.800.000. Baris lainnya adalah contoh pilot yang dibuat untuk demo, bukan klaim paket nyata.

Untuk memakai data nyata, unduh CSV dari data.inaproc.id/rup dengan filter tahun, jenis instansi, dan instansi yang dipilih, lalu ganti file contoh dengan file tersebut dan pastikan nama kolom Anggaran-nya sama. Kolom provinsi dan kabupaten_kota pada file contoh ditambahkan untuk peta pilot, karena tabel Anggaran di halaman tersebut tidak menampilkan kolom lokasi secara langsung; lokasi detail tiap paket ada di halaman detail SIRUP atau SPSE.

Sumber yang sudah dicek live pada 27 Oktober 2026:

- SIRUP publik sekarang di sirup.inaproc.id/sirup, domain lama sirup.lkpp.go.id sudah tidak bisa dibuka. Pencarian paket publik bisa tanpa login.
- SPSE Nasional di spse.inaproc.id/nasional, pencarian tender publik bisa tanpa login, dengan detail pagu, HPS, peserta, dan jadwal.
- Data Inaproc di data.inaproc.id/rup, tombol Download CSV hanya aktif setelah memilih tahun, jenis instansi, dan instansi, jadi tidak ada unduhan nasional sekali klik. Data terakhir tersinkron 26 Oktober 2026 pukul 02.38 WIB pada saat pengecekan.
- Tidak ditemukan API publik resmi di halaman-halaman tersebut pada saat pengecekan.

## Fitur MVP Pilot

- Pencarian paket berdasarkan kata kunci, metode, provinsi, dan status berbendera
- Ringkasan total paket, total nilai, rata-rata nilai, dan jumlah paket berbendera
- Peta agregat per provinsi dengan Leaflet dan OpenStreetMap, titiknya adalah agregat provinsi, bukan lokasi persis tiap paket
- Empat bendera anomali yang transparan, lihat bagian berikutnya
- API REST dan CLI untuk ringkasan, daftar, dan pencarian

## Bendera Anomali

| Kode | Aturan | Makna |
| --- | --- | --- |
| pagu_besar | Total nilai >= Rp 1.000.000.000 | Paket besar yang layak diprioritaskan untuk dicek |
| paket_serupa_berulang | Minimal 3 paket dengan 4 kata awal nama yang sama di satker yang sama | Perlu dicek apakah tahapan sah atau pemecahan paket |
| nilai_bulat | Total nilai >= Rp 100.000.000 dan kelipatan Rp 10.000.000 | Bisa jadi pembulatan perencanaan yang sah, bisa jadi perkiraan tanpa rincian |
| penunjukan_langsung_besar | Metode Penunjukan Langsung dan total nilai >= Rp 200.000.000 | Perlu dicek dasar penunjukan karena tanpa kompetisi terbuka |

Semua bendera menampilkan penjelasan dan ambang di API dan di halaman web saat kursor diarahkan ke label bendera.

## Menjalankan Project

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Buka http://127.0.0.1:8000/ untuk dashboard, dan http://127.0.0.1:8000/docs untuk dokumentasi API.

## Memakai CLI

```bash
python cli.py summary
python cli.py list --flagged-only
python cli.py search --q laboratorium
```

## Endpoint API

| Method | Endpoint | Fungsi |
| --- | --- | --- |
| GET | / | Dashboard web |
| GET | /health | Cek status server |
| GET | /api/summary | Ringkasan dataset |
| GET | /api/packages | Daftar paket dengan filter q, metode, provinsi, hanya_berbendera |
| GET | /api/map | Titik agregat per provinsi untuk peta |

## Struktur Project

```
app/
  main.py     Aplikasi FastAPI
  loader.py   Pembaca CSV format RUP Anggaran
  flags.py    Aturan bendera anomali dan ringkasan
data/
  sample_kemenkes_2026.csv  Data contoh pilot, 24 baris
frontend/
  index.html  Dashboard dengan peta Leaflet
cli.py        Antarmuka command line
tests/        Unit test dan test API
```

## Menjalankan Test

```bash
pytest -q
```

## Roadmap

- Ganti data contoh dengan CSV ekspor nyata per instansi, dan dokumentasikan tanggal sinkron tiap impor
- Tambah lokasi detail dari halaman SIRUP atau SPSE untuk peta per paket, bukan hanya agregat provinsi
- Tambah bendera selisih pagu dan HPS dari data SPSE, serta jumlah peserta tender
- Parsing berita acara penetapan pemenang PDF untuk bendera pemenang berulang, di fase terpisah karena datanya tidak tersedia sebagai field HTML
- Laporan anomali mingguan untuk redaksi media, LSM, dan akademisi

## Batasan yang Disadari

Project ini memakai data rencana pengadaan, bukan hasil akhir kontrak untuk semua paket. Harga menang dan pemenang berkontrak tidak selalu tersedia sebagai field yang mudah dibaca, dan unduhan CSV hanya per instansi, bukan nasional sekali klik. Klaim realtime tidak dipakai, yang dipakai adalah tanggal sinkron terakhir dari sumber.

## Author

**Ade Bintang**

Mahasiswa Informatika Universitas Gunadarma dengan fokus pada AI Engineering dan Data Science.

GitHub: [@kerb0y](https://github.com/kerb0y)

## License

MIT License. Lihat file LICENSE untuk detailnya.
