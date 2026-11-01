# SOLARNESIA: Model Spasial Berbasis Komputer Grafis untuk Analisis Distribusi dan Penetapan Prioritas Pembangkit Listrik Tenaga Surya Nasional

> **AFL 2 Proyek Komputer Grafis (IMT01303501 - 3 SKS)**  
> **Program Studi Informatika, Universitas Ciputra Surabaya (Semester Gasal 2026/2027)**  
> **Dosen Pengampu:** Citra Lestari, S.Kom., M.Kom.

---

## 👥 Tim Penyusun (Kelompok 6)

| No | Nama | NIM | Email |
| :---: | :--- | :---: | :--- |
| 1 | **Wesley Goeinawan** | 0706012410011 | `wgoeinawan01@student.ciputra.ac.id` |
| 2 | **Stevanus Ivan Santoso** | 0706012410029 | `ssantoso04@student.ciputra.ac.id` |
| 3 | **Nicholas Gerwin Mawardji** | 0706012410015 | `nmawardji@student.ciputra.ac.id` |

---

## ☀️ Deskripsi Proyek

**Solarnesia** adalah sistem pendukung keputusan spasial berbasis visualisasi grafis interaktif yang memadukan data potensi radiasi surya (Global Solar Atlas), toleransi termal lingkungan, dan analisis kedekatan geometris permukiman penduduk di seluruh kepulauan Indonesia.

### 🌟 Fitur Utama & Pipeline Grafis (AFL 2)
1. **Layer 1 (2D MultiPolygons & Choropleth):** Peta dasar batas wilayah 34 provinsi (GeoJSON) dengan gradasi warna potensi radiasi surya tahunan (*Photovoltaic Power Output* / $PV_{OUT}$) yang dapat diatur melalui kontrol panel layer interaktif.
2. **Layer 2 (0D Points & Masking):**
   - **Pemotongan Spasial (*Spatial Clip*):** Mengeliminasi 1.160 titik laut, menyisakan **3.802 titik darat murni**.
   - **Seleksi Tapak Teknis PLTS:** Menyaring **513 kandidat tapak potensial** ($PV_{OUT} \ge 1.430\text{ kWh/kWp}$, $\text{TEMP} \le 27,5^\circ\text{C}$).
   - **Pembersihan Memori Efisien:** Secara proaktif menghapus layer mentah dari RAM (`del df_raw, raw_pts, land_sj`) untuk meringankan beban rendering visual.
3. **5 km Proximity Hotspot Clustering (DBSCAN):**
   - Mengelompokkan titik kandidat dalam radius $\le 5\text{ km}$ menggunakan `DBSCAN(eps=5000)` menjadi **480 sentra energi surya terpadu** (termasuk 31 klaster multi-titik) guna mencegah duplikasi pembangunan gardu induk transmisi.
4. **Zona Penyangga Metrik (*Buffer 25 km*):**
   - Proyeksi EPSG:3857 dengan koreksi distorsi Mercator $\cos(\text{lat})$ untuk koridor transmisi distribusi **25 km** `buffer(25000)` sesuai standar teknis keandalan PLN Saluran Udara Tegangan Menengah (SUTM 20 kV).
5. **Analisis Keterjangkauan Spasial (*Spatial Join*):**
   - Menguji keterjangkauan terhadap **7.217 titik pusat permukiman kecamatan BPS nasional**:
     - **2.806 kecamatan (38,9%)** terlayani dalam koridor transmisi 25 km.
     - **4.411 kecamatan (61,1%)** berada di luar jangkauan (off-grid / target mikrogrid surya mandiri).
   - Menjangkau **294 kabupaten/kota** dari total 514 daerah di Indonesia.
6. **Peta Interaktif Folium Terpadu (*Interactive Visualizer*):**
   - Visualisasi berbasis Folium/Leaflet yang dirender mandiri di dalam sel notebook dan diekspor otomatis ke `outputs/solarnesia_interactive_map.html`.
   - Multi-layer switchable: Koroplet Provinsi 34 Daerah, Tapak Sentra PLTS 5 km, Koridor Transmisi 25 km, Klaster Kecamatan Terjangkau (Emerald Cluster), Klaster Off-Grid (Slate Cluster), serta Popup Inspeksi Klik interaktif per sentra PLTS.

---

## 📊 Hasil Analisis Spasial Keterjangkauan Permukiman (Tabel 1)

| Parameter Teknis Jaringan | Total Populasi Kecamatan | Kecamatan Terjangkau Feeder | Kecamatan Off-Grid | Status / Standar Acuan |
| :--- | :---: | :---: | :---: | :--- |
| **Radius Buffer 25 km** | **7.217 titik** | **2.806 kecamatan (38,9%)** | **4.411 kecamatan (61,1%)** | **Standar Resmi Keandalan Saluran Distribusi 20 kV PLN** |

*Catatan: Hasil analisis ringkasan otomatis diekspor ke `outputs/solarnesia_table1_summary.csv`.*

---

## 📁 Struktur Berkas

```text
Solarnesia_AFL2/
├── solarnesia_afl2.ipynb                     # Notebook utama (pipeline bersih, efisien & mandiri)
├── solarnesia_afl2 comment.ipynb             # Notebook beranotasi penjelasan baris per baris
├── solarnesia_code_architecture_plan.md      # Dokumen arsitektur dan spesifikasi teknis
├── README.md                                 # Dokumentasi proyek & instruksi eksekusi
├── requirements.txt                          # Dependensi pustaka Python
├── outputs/                                  # Folder hasil ekspor otomatis
│   ├── solarnesia_table1_summary.csv         # Ekspor tabel metrik keterjangkauan
│   └── solarnesia_interactive_map.html       # Ekspor peta interaktif mandiri (dapat dibuka di browser)
└── data/
    ├── indonesia_solar_data.csv              # 4.962 titik observasi Global Solar Atlas
    ├── indonesia_provinces.geojson           # Batas poligon 34 provinsi (Layer 1 Koroplet)
    ├── indonesia_kabupaten.geojson           # Batas poligon 514 kabupaten/kota (Spatial clip & admin join)
    └── indonesia_kecamatan.csv               # 7.217 titik pusat kecamatan BPS (Titik demand permukiman riil)
```

---

## 🚀 Panduan Menjalankan

### Prasyarat
Pastikan Python 3.10+ telah terpasang dengan pustaka berikut:
```bash
pip install -r requirements.txt
```

### Eksekusi Notebook
1. Buka `solarnesia_afl2.ipynb` menggunakan **VS Code**, **JupyterLab**, atau **Jupyter Notebook**.
2. Jalankan sel dari atas ke bawah (*Run All*).
3. Sel 8 akan menampilkan ringkasan data Tabel 1 dan mengekspor CSV, dan Sel 9 akan langsung merender peta interaktif di dalam layar kerja serta mengekspor file HTML mandiri.
