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

**Solarnesia** adalah sistem pendukung keputusan spasial berbasis visualisasi grafis 2D yang memadukan data potensi radiasi surya (Global Solar Atlas), toleransi termal lingkungan, dan analisis kedekatan geometris permukiman di seluruh kepulauan Indonesia.

### 🌟 Fitur Utama
1. **Layer 1 (2D MultiPolygons & Choropleth):** Peta dasar daratan provinsi dan kabupaten terbuka (GeoJSON) dengan gradasi warna potensi radiasi surya tahunan (*Photovoltaic Power Output* / $PV_{OUT}$).
2. **Layer 2 (0D Points & Buffers):**
   - **Pemotongan Spasial (*Spatial Clip*):** Mengeliminasi 1.160 titik laut, menyisakan 3.802 titik darat murni.
   - **Seleksi Tapak PLTS:** Menyaring 513 kandidat tapak potensial ($PV_{OUT} \ge 1.430\text{ kWh/kWp}$, $\text{TEMP} \le 27,5^\circ\text{C}$).
   - **5 km Hotspot Clustering:** Mengelompokkan titik kandidat dalam radius 5 km (`DBSCAN`) menjadi 480 sentra energi terintegrasi (31 klaster multi-titik).
   - **Zona Penyangga (*Buffer*):** Proyeksi EPSG:3857 dengan koreksi distorsi Mercator $\cos(\text{lat})$ untuk *footprint* tapak 3 km `buffer(3000)` dan koridor transmisi 25 km `buffer(25000)` sesuai standar teknis PLN Tegangan Menengah 20 kV.
3. **Analisis Keterjangkauan (*Spatial Join*):**
   - Menguji 3.289 titik demand permukiman darat: **325 permukiman (9,9%)** terjangkau dalam koridor 25 km, sedangkan **2.964 titik (90,1%)** berada di luar jangkauan (membuktikan perlunya sistem PLTS mikrogrid mandiri/kabel laut di pulau terpencil).
   - Menjangkau **294 kabupaten/kota** dari total 519 daerah di Indonesia.
4. **Inspeksi Interaktif (*Clickable Map*):** Peta interaktif berbasis Folium/Leaflet yang memungkinkan pengguna mengklik titik manapun (contoh: Bali Selatan) untuk melihat informasi $PV_{OUT}$, temperatur, dan daftar lengkap kecamatan/kabupaten yang masuk dalam radius 25 km.

---

## 📊 Hasil Analisis Spasial (Tabel 1)

| Radius Buffer | Permukiman Terjangkau | Persentase | Status / Keterangan |
| :--- | :---: | :---: | :--- |
| **10 km** | 49 titik | 1,5% | Skenario Sensitivitas (Jangkauan Pendek Padat) |
| **25 km** | **325 titik** | **9,9%** | **Standar Resmi Operasional Distribusi TM 20 kV PLN** |
| **40 km** | 605 titik | 18,4% | Skenario Sensitivitas (Ekspansi Interkoneksi) |

---

## 📁 Struktur Berkas

```text
Solarnesia_AFL2/
├── solarnesia_afl2.ipynb                     # Notebook utama (12 sel terstruktur top-to-bottom)
├── solarnesia_code_architecture_plan.md      # Dokumen arsitektur dan spesifikasi teknis
├── data/
│   ├── indonesia_solar_data.csv              # 4.962 titik observasi Global Solar Atlas
│   ├── indonesia_provinces.geojson           # Batas poligon 34 provinsi (Layer 1)
│   └── indonesia_kabupaten.geojson           # Batas poligon 519 kabupaten/kota (Spatial join)
└── outputs/
    ├── solarnesia_coverage_map.png           # Gambar publikasi 2D resolusi tinggi
    ├── solarnesia_interactive_map.html       # Peta web interaktif (inspeksi klik)
    ├── solarnesia_table1_summary.csv         # Ringkasan data metrik Tabel 1
    └── solarnesia_covered_kabupaten.csv      # Daftar 294 kabupaten/kota terlayani
```

---

## 🚀 Panduan Menjalankan

### Prasyarat
Pastikan Python 3.10+ telah terpasang dengan pustaka berikut:
```bash
pip install geopandas pandas matplotlib shapely scikit-learn folium mapclassify
```

### Eksekusi Notebook
1. Buka `solarnesia_afl2.ipynb` menggunakan **Jupyter Notebook**, **JupyterLab**, atau **VS Code**.
2. Jalankan sel dari atas ke bawah (*Run All*).
3. Buka `outputs/solarnesia_interactive_map.html` di peramban web untuk menjelajahi peta interaktif.
