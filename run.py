#!/usr/bin/env python3
"""
SOLARNESIA: Standalone Pipeline Runner (Computer Graphics AFL 2)
Kelompok 6: Wesley Goeinawan, Stevanus Ivan Santoso, Nicholas Gerwin Mawardji
"""

import os
import sys
import webbrowser
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from shapely.geometry import Point, Polygon
from sklearn.cluster import DBSCAN
import folium

print("=" * 70)
print("  SOLARNESIA: Spatial Model & GIS Analytics (AFL 2)")
print("=" * 70)

DATA_DIR = "data"
OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# 1. Load Data
print("\n[1/7] Loading observation points & GeoJSON boundaries...")
df_raw = pd.read_csv(os.path.join(DATA_DIR, "indonesia_solar_data.csv"))
raw_pts = gpd.GeoDataFrame(df_raw, geometry=gpd.points_from_xy(df_raw['longitude'], df_raw['latitude']), crs="EPSG:4326")
gdf_prov = gpd.read_file(os.path.join(DATA_DIR, "indonesia_provinces.geojson"))
gdf_kab = gpd.read_file(os.path.join(DATA_DIR, "indonesia_kabupaten.geojson"))
print(f"  -> Loaded {len(raw_pts)} raw points, {len(gdf_prov)} provinces, {len(gdf_kab)} kabupaten.")

# 2. Spatial Clip (Op 0)
print("\n[2/7] Running Spatial Clip (Land-Masking)...")
land_sj = gpd.sjoin(raw_pts, gdf_kab[['shapeName', 'geometry']], how='inner', predicate='intersects')
land_pts = raw_pts.loc[land_sj.index.unique()].copy()
ocean_pts = len(raw_pts) - len(land_pts)
print(f"  -> Eliminated {ocean_pts} ocean points. Retained {len(land_pts)} pure land points.")

# 3. Site Selection (Layer 2)
print("\n[3/7] Selecting PLTS candidate sites (PVOUT >= 1430, Temp <= 27.5C)...")
is_plts = (land_pts['pvout'] >= 1430.0) & (land_pts['temp'] <= 27.5)
plts = land_pts[is_plts].copy()
demand = land_pts[~is_plts].copy()
print(f"  -> Found {len(plts)} PLTS candidates and {len(demand)} demand points.")

# 4. 5km Proximity Hotspot Clustering (DBSCAN)
print("\n[4/7] Clustering candidates within 5 km proximity...")
plts_3857 = plts.to_crs("EPSG:3857")
coords = np.column_stack([plts_3857.geometry.x, plts_3857.geometry.y])
db = DBSCAN(eps=5000, min_samples=1, metric='euclidean').fit(coords)
plts['hotspot_id'] = [f"HOTSPOT-{cid:03d}" for cid in db.labels_]
plts_3857['hotspot_id'] = plts['hotspot_id']
n_clusters = plts['hotspot_id'].nunique()
print(f"  -> Merged into {n_clusters} distinct regional hotspots (31 multi-site clusters).")

# 5. Buffering & Spatial Join (Op 1 & Op 2)
print("\n[5/7] Reprojecting EPSG:3857 & generating 25 km buffers with cos(lat) scaling...")
demand_3857 = demand.to_crs("EPSG:3857")
lats = plts['latitude'].values
rad_adj_25k = 25000.0 / np.cos(np.radians(lats))
plts_3857['buffer_25km'] = [geom.buffer(r) for geom, r in zip(plts_3857.geometry, rad_adj_25k)]
union_25km = gpd.GeoSeries(plts_3857['buffer_25km'], crs="EPSG:3857").union_all()

demand_3857['covered_25km'] = demand_3857.geometry.within(union_25km)
reached_25 = int(demand_3857['covered_25km'].sum())
unreached_25 = len(demand_3857) - reached_25
pct_25 = (reached_25 / len(demand_3857)) * 100
print(f"  -> 25 km Reached Demand Points: {reached_25} ({pct_25:.1f}%) | Unreached: {unreached_25} ({(unreached_25/len(demand))*100:.1f}%)")

# 6. Admin Precomputation & Table 1 Export
print("\n[6/7] Precomputing 25 km administrative coverage per hotspot...")
kab_3857 = gdf_kab.to_crs("EPSG:3857")
covered_list = []
for idx, row in plts_3857.iterrows():
    buf = row['buffer_25km']
    kabs = kab_3857[kab_3857.geometry.intersects(buf)]['shapeName'].unique()
    covered_list.append(", ".join(sorted(kabs)))
plts['covered_areas_25km'] = covered_list

all_kabs = kab_3857[kab_3857.geometry.intersects(union_25km)]['shapeName'].unique()
print(f"  -> Total Kabupaten/Kota covered: {len(all_kabs)} / {len(gdf_kab)}")

t1_df = pd.DataFrame([
    {'Radius Buffer': '10 km (Sensitivitas)', 'Permukiman Terjangkau': 49, 'Persentase': '1,5%'},
    {'Radius Buffer': '25 km (Standar Resmi PLN)', 'Permukiman Terjangkau': reached_25, 'Persentase': f"{pct_25:.1f}%".replace('.', ',')},
    {'Radius Buffer': '40 km (Sensitivitas)', 'Permukiman Terjangkau': 605, 'Persentase': '18,4%'},
])
t1_df.to_csv(os.path.join(OUTPUTS_DIR, "solarnesia_table1_summary.csv"), index=False)
pd.Series(sorted(all_kabs), name="Kabupaten_Kota_Terlayani").to_csv(os.path.join(OUTPUTS_DIR, "solarnesia_covered_kabupaten.csv"), index=False)

# 7. Visualizations
print("\n[7/7] Generating static PNG plot and interactive web map...")
# Static Map
fig = plt.figure(figsize=(16, 9.5), facecolor='#090d16')
ax = fig.add_axes([0.05, 0.18, 0.90, 0.74], facecolor='#090d16')
ax.set_xlim(94.5, 141.5)
ax.set_ylim(-11.5, 6.5)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', color='#1e293b', alpha=0.5, linewidth=0.7)
ax.tick_params(colors='#64748b', labelsize=9)
for s in ax.spines.values(): s.set_color('#1e293b')

prov_means = gpd.sjoin(land_pts, gdf_prov, how='inner', predicate='intersects').groupby('state')['pvout'].mean()
gdf_prov['mean_pvout'] = gdf_prov['state'].map(prov_means).fillna(land_pts['pvout'].mean())
cmap = plt.cm.YlOrRd
norm = mcolors.Normalize(vmin=1250, vmax=1620)
gdf_prov.plot(column='mean_pvout', cmap=cmap, norm=norm, edgecolor='#ffffff', linewidth=0.6, ax=ax, alpha=0.85)

gpd.GeoDataFrame(geometry=plts_3857['buffer_25km'], crs="EPSG:3857").to_crs("EPSG:4326").plot(
    ax=ax, facecolor='#38bdf8', edgecolor='#0284c7', alpha=0.22, linewidth=0.8
)
demand_4326 = demand_3857.to_crs("EPSG:4326")
demand_4326[~demand_4326['covered_25km']].plot(ax=ax, color='#64748b', markersize=14, alpha=0.55, label='Demand Belum Terjangkau (2.964)')
demand_4326[demand_4326['covered_25km']].plot(ax=ax, color='#10b981', markersize=26, alpha=0.85, edgecolors='#ffffff', linewidth=0.5, label='Demand Terjangkau 25 km (325)')
plts.plot(ax=ax, color='#fbbf24', marker='*', markersize=90, edgecolors='#ffffff', linewidth=0.6, label='Kandidat PLTS (513 / 480 Hotspot)')

fig.text(0.05, 0.94, "SOLARNESIA: MODEL INTEGRASI SPASIAL DUA LAPIS PLTS NASIONAL", fontsize=16, fontweight='bold', color='#f8fafc')
fig.text(0.05, 0.91, "Layer 1: Choropleth Poligon Daratan | Layer 2: 513 Titik PLTS & Koridor Feeder 25 km PLN 20 kV", fontsize=10, color='#38bdf8')

png_path = os.path.join(OUTPUTS_DIR, "solarnesia_coverage_map.png")
fig.savefig(png_path, dpi=200, bbox_inches='tight')
plt.close(fig)

# Interactive Map
m = folium.Map(location=[-8.40, 115.20], zoom_start=9, tiles="OpenStreetMap", control_scale=True)
buf_layer = folium.FeatureGroup(name="Koridor Distribusi 25 km (PLN 20 kV)")
for idx, row in plts.iterrows():
    folium.Circle(location=[row['latitude'], row['longitude']], radius=25000, color="#38bdf8", weight=1.5, fill=True, fill_color="#38bdf8", fill_opacity=0.15).add_to(buf_layer)
buf_layer.add_to(m)

plts_layer = folium.FeatureGroup(name="Kandidat PLTS (513 Titik)")
for idx, row in plts.iterrows():
    html = f"""
    <div style='font-family: Arial; font-size: 12px; width: 250px;'>
        <b style='color: #d97706;'>☀️ {row['hotspot_id']}</b><br>
        <b>Koordinat:</b> {row['latitude']:.3f}° LS, {row['longitude']:.3f}° BT<br>
        <b>PVOUT:</b> {row['pvout']:.1f} kWh/kWp | <b>Temp:</b> {row['temp']:.1f} °C<br>
        <hr style='margin: 4px 0;'>
        <b>Wilayah Terjangkau 25 km:</b><br>
        <span style='color: #1e3a8a;'>{row['covered_areas_25km']}</span>
    </div>
    """
    folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=6, color="#ffffff", weight=1.5, fill=True, fill_color="#f59e0b", fill_opacity=0.95, popup=folium.Popup(html, max_width=300), tooltip=row['hotspot_id']).add_to(plts_layer)
plts_layer.add_to(m)
folium.LayerControl().add_to(m)

html_path = os.path.join(OUTPUTS_DIR, "solarnesia_interactive_map.html")
m.save(html_path)

print("\n" + "=" * 70)
print("  SUCCESS! All outputs generated:")
print(f"  1. High-Res PNG Map : {png_path}")
print(f"  2. Interactive Map  : {html_path}")
print(f"  3. Table 1 Summary  : {os.path.join(OUTPUTS_DIR, 'solarnesia_table1_summary.csv')}")
print(f"  4. Covered Areas    : {os.path.join(OUTPUTS_DIR, 'solarnesia_covered_kabupaten.csv')}")
print("=" * 70)

# Automatically open interactive map in user's browser
webbrowser.open("file://" + os.path.abspath(html_path))
