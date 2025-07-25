from function.nav import Nav
from sklearn.preprocessing import StandardScaler
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import streamlit as st
import pandas as pd
from function.maps import add_logo
import os
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static, st_folium
import folium
import pandas as pd
from geopy.geocoders import ArcGIS
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import numpy as np
from pathlib import Path
from streamlit_extras.metric_cards import style_metric_cards
import io
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from folium.plugins import MarkerCluster, FeatureGroupSubGroup
from scipy.spatial import ConvexHull, QhullError
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="🌍 Maps Clustering PMB UKDW",
    layout="wide"
)
from function.clustering_utils import (
    load_cleaned_data,
    normalize_data,
    aggregate_and_score,
    calculate_weighted_score,
    get_cluster_color,
    calculate_choice1_count,
    calculate_choice2_count,
    calculate_lulus_seleksi,
    calculate_registrasi,
    merge_all_metrics,
    process_filtered_data,
    kmeans_per_region,
    process_filtered_data,
    cluster_program_study_by_province,
    kmeans_cluster_program_province,
    cluster_program_study_by_city,
    kmeans_cluster_program_city,
    cluster_by_province,
    kmeans_cluster_province,
    cluster_by_city_in_province,
    kmeans_cluster_city,
    generate_labels_for_clusters,
    get_df_hash,
)

def main():
    # Cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        Nav("clustering")
        st.stop()
    Nav("clustering")
    pd.set_option('display.max_columns', None)

    add_logo()

    # Pastikan file 'cleaned_data.xlsx' ada sebelum memuat data
    cleaned_df = load_cleaned_data()
    if cleaned_df.empty:
        st.error("Data tidak ditemukan. Pastikan file 'cleaned_data.xlsx' tersedia di folder 'uploaded_files'.")
        st.stop()
    else:
         # Normalisasi Nama Provinsi untuk konsistensi
        cleaned_df['prop_sek'] = cleaned_df['prop_sek'].str.strip().str.upper()
        filters = st.session_state.get("clustering", {})  # ambil filter khusus halaman 'home'
        provinsi_filter = filters.get('provinsi_filter', "SEMUA PROVINSI")
        kabupaten_filter = filters.get('kabupaten_filter', "SEMUA KABUPATEN")
        program_studi_filter = filters.get('program_studi_filter', None)
        tahun_filter = filters.get("tahun_filter", list(cleaned_df['tahun'].unique()))
        cluster_sekolah = filters.get('jumlah_cluster_sekolah', 2)
        cluster_kota = filters.get('jumlah_cluster_kota', 2)
        cluster_provinsi = filters.get('jumlah_cluster_provinsi', 2)

        filtered_df = cleaned_df.copy()

        if program_studi_filter != "Tidak Ada":
            filtered_df = cleaned_df[
                (cleaned_df['pilihan1'] == program_studi_filter) |
                (cleaned_df['pilihan2'] == program_studi_filter)
            ]
            filtered_df = filtered_df.copy()  # Tambahkan ini agar .loc/assignment aman
            filtered_df["program_studi"] = program_studi_filter
        else:
            # Jika filter = "Tidak Ada", kita tetap harus buat kolom program_studi agar tidak error
            filtered_df = cleaned_df.copy()
            filtered_df["program_studi"] = filtered_df["pilihan1"]  # atau default value lain
        # Filter provinsi
        if provinsi_filter == "Non-DIY&JATENG":
            filtered_df = cleaned_df[~cleaned_df['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])]
        elif provinsi_filter == "SEMUA PROVINSI":
            filtered_df = cleaned_df.copy()
        else:
            filtered_df = cleaned_df[cleaned_df['prop_sek'] == provinsi_filter]

        # Filter kabupaten jika dipilih
        if kabupaten_filter != "SEMUA KABUPATEN":
            filtered_df = filtered_df[filtered_df['kota_sek'] == kabupaten_filter]

        # Filter tahun
        if tahun_filter:
            filtered_df = filtered_df[filtered_df['tahun'].isin(tahun_filter)]

        df_hash = get_df_hash(filtered_df)

        # Hitung skor berbobot (juga sebaiknya dibuat cached, seperti calculate_weighted_score_cached())
        final_data, grouped_data_normalized = calculate_weighted_score(filtered_df, df_hash)

        # Merge untuk tambahkan lat/lon
        final_data = final_data.merge(
            filtered_df[['nama_sekolah', 'kota_sek', 'prop_sek', 'latitude', 'longitude', 'tahun']],
            on=['nama_sekolah', 'kota_sek', 'prop_sek'],
            how='left'
        ).drop_duplicates(subset=['nama_sekolah', 'kota_sek', 'prop_sek'])

        # Jalankan KMeans yang dicache
        final_data, iteration_results_schools = kmeans_per_region(final_data, cluster_sekolah, df_hash)


        # Hitung jarak minimum ke centroid dalam lingkup provinsi & kota
        final_data['Jarak_Minimum'] = -1
        for result in iteration_results_schools:
            if len(result["centroids"]) == 0:
                continue  # Lewati kota dengan hanya satu sekolah (tidak bisa dihitung centroid)
            
            centroids = np.array(result["centroids"])
            mask = (final_data['prop_sek'] == result["provinsi"]) & (final_data['kota_sek'] == result["kota"])
            local_data = final_data.loc[mask, ['skor_akhir_normalized']].to_numpy()

            # Hitung jarak setiap sekolah ke centroidnya
            distances = np.array([np.linalg.norm(local_data - centroid, axis=1) for centroid in centroids]).T
            final_data.loc[mask, 'Jarak_Minimum'] = np.min(distances, axis=1)

        # Simpan centroid dan jarak ke centroid ke final_data
        for result in iteration_results_schools:
            mask = (final_data['prop_sek'] == result["provinsi"]) & (final_data['kota_sek'] == result["kota"])
            if len(result["centroids"]) >= 2:
                for i, centroid in enumerate(result["centroids"]):
                    final_data.loc[mask, f'Centroid_{i}'] = centroid
                    final_data.loc[mask, f'Jarak_Centroid_{i}'] = np.abs(final_data.loc[mask, 'skor_akhir_normalized'] - centroid)


        # Labelkan sekolah berdasarkan clustering di provinsi & kota masing-masing
        final_data['potensi'] = 'Tidak Potensial'
        for result in iteration_results_schools:
            if len(result["centroids"]) == 0:
                continue

            centroids = result["centroids"]
            mask = (final_data['prop_sek'] == result["provinsi"]) & (final_data['kota_sek'] == result["kota"])

            # Tentukan label untuk masing-masing cluster berdasarkan centroid
            centroid_labels = generate_labels_for_clusters(len(centroids), centroids)
            final_data.loc[mask, 'potensi'] = final_data.loc[mask, 'Cluster'].map(centroid_labels)

        # Hitung hash dari final_data untuk cache cluster_by_province
        df_hash_prov = get_df_hash(final_data)

        # Cluster provinsi
        province_data = cluster_by_province(final_data, df_hash_prov)

        # Hash ulang untuk input clustering provinsi
        df_hash_province_cluster = get_df_hash(province_data)

        # Jalankan clustering jika diperlukan
        if provinsi_filter in ["SEMUA PROVINSI", "Non-DIY&JATENG"]:
            province_clustered, province_centroids = kmeans_cluster_province(
                province_data,
                optimal_clusters=cluster_provinsi,
                df_hash=df_hash_province_cluster
            )
        else:
            # Tidak clustering, beri label dummy dan lengkapi kolom agar tidak error
            province_data["Label_Cluster_Prov"] = "Tanpa Klaster"
            province_data["total_score_normalized"] = 0  # atau bisa pakai nilai asli
            province_data["Label_Cluster"] = "Tanpa Klaster"
            province_data["Cluster"] = -1  # cluster dummy
            province_clustered = province_data.copy()
            province_centroids = None

        # Hitung hash dari final_data untuk cache cluster_by_city_in_province
        df_hash_city = get_df_hash(final_data)

        # Buat data agregat kota
        city_data = cluster_by_city_in_province(final_data, df_hash_city)

        # Hitung hash ulang untuk cache proses kmeans kota
        df_hash_city_cluster = get_df_hash(city_data)

        # Jalankan clustering kota hanya jika kabupaten tidak difilter
        if kabupaten_filter == "SEMUA KABUPATEN":
            city_clustered = kmeans_cluster_city(city_data, cluster_kota, df_hash=df_hash_city_cluster)
        else:
            # Buat dummy cluster seperti pada provinsi
            city_data["Label_Cluster"] = "Tanpa Klaster"
            city_data["Cluster"] = -1
            city_data["total_score_normalized"] = 0
            city_clustered = city_data.copy()
    
        clustered_data, iteration_results_prodi = process_filtered_data(filtered_df, cluster_sekolah)
        clustered_data = clustered_data.drop_duplicates(subset=['nama_sekolah', 'kota_sek', 'prop_sek', 'program_studi'])

        # Hitung jarak minimum ke centroid dalam lingkup provinsi & kota
        clustered_data['Jarak_Minimum'] = -1
        for result in iteration_results_prodi:
            if len(result["centroids"]) == 0:
                continue  # Lewati kota dengan hanya satu sekolah (tidak bisa dihitung centroid)

            centroids = np.array(result["centroids"])
            mask = (clustered_data['prop_sek'] == result["provinsi"]) & (clustered_data['kota_sek'] == result["kota"])
            local_data = clustered_data.loc[mask, ['skor_normalized']].to_numpy()

            # Hitung jarak setiap sekolah ke centroidnya
            distances = np.array([np.linalg.norm(local_data - centroid, axis=1) for centroid in centroids]).T
            clustered_data.loc[mask, 'Jarak_Minimum'] = np.min(distances, axis=1)
            

        # Simpan centroid dan jarak ke centroid ke clustered_data
        for result in iteration_results_prodi:
            mask = (clustered_data['prop_sek'] == result["provinsi"]) & (clustered_data['kota_sek'] == result["kota"])
            if len(result["centroids"]) >= 2:
                for i, centroid in enumerate(result["centroids"]):
                    clustered_data.loc[mask, f'Centroid_{i}'] = centroid
                    clustered_data.loc[mask, f'Jarak_Centroid_{i}'] = np.abs(clustered_data.loc[mask, 'skor_normalized'] - centroid)

        # Labelkan program studi berdasarkan clustering di provinsi & kota masing-masing
        clustered_data['potensi'] = 'Tidak Potensial'
        for result in iteration_results_prodi:
            if len(result["centroids"]) == 0:
                continue

            centroids = result["centroids"]
            mask = (clustered_data['prop_sek'] == result["provinsi"]) & (clustered_data['kota_sek'] == result["kota"])

            # Tentukan label untuk masing-masing cluster berdasarkan centroid
            centroid_labels = generate_labels_for_clusters(len(centroids), centroids)
            clustered_data.loc[mask, 'potensi'] = clustered_data.loc[mask, 'Cluster'].map(centroid_labels)
        # Clustering provinsi
        province_data_prodi = cluster_program_study_by_province(clustered_data)

        # Proses clustering hanya untuk SEMUA PROVINSI dan Non-DIY&JATENG
        if provinsi_filter in ["SEMUA PROVINSI", "Non-DIY&JATENG"]:
            province_clustered_prodi = kmeans_cluster_program_province(province_data_prodi, optimal_clusters=cluster_provinsi)
        else:
             # Tidak clustering, hanya beri label dummy
            province_data_prodi["Label_Cluster_Prov"] = "Tanpa Klaster"
            province_data_prodi["total_score_normalized"] = 0  # atau bisa pakai nilai asli
            province_data_prodi["Label_Cluster"] = "Tanpa Klaster"
            province_data_prodi["Cluster"] = -1  # cluster dummy
            province_clustered_prodi = province_data_prodi.copy()
            province_centroids = None

        # Clustering kota
        city_data_prodi = cluster_program_study_by_city(clustered_data)
        # Clustering kota hanya jika semua kabupaten
        if kabupaten_filter == "SEMUA KABUPATEN":
            city_clustered_prodi = kmeans_cluster_program_city(city_data_prodi, cluster_kota)
        else:
            # Buat dummy cluster seperti pada provinsi
            city_data_prodi["Label_Cluster"] = "Tanpa Klaster"
            city_data_prodi["Cluster"] = -1
            city_data_prodi["total_score_normalized"] = 0
            city_clustered_prodi = city_data_prodi.copy()

        # Display results in the next section
        if cleaned_df is not None:
            # Gunakan hasil clustering sesuai program studi jika dipilih
            if program_studi_filter != "Tidak Ada":
                # Filter data hasil clustering program studi sesuai filter
                filtered_map_data = clustered_data[clustered_data['program_studi'] == program_studi_filter].copy()
                
                # Pastikan hanya data dengan koordinat valid yang dipakai
                filtered_map_data['latitude'] = pd.to_numeric(filtered_map_data['latitude'], errors='coerce')
                filtered_map_data['longitude'] = pd.to_numeric(filtered_map_data['longitude'], errors='coerce')
                filtered_map_data = filtered_map_data.dropna(subset=['latitude', 'longitude'])

                # --- PROVINSI ---
                prov_merge_cols = [col for col in province_clustered_prodi.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                prov_merge_cols += ['prop_sek', 'total_score_normalized', 'Label_Cluster', 'Cluster']

                province_clustered_renamed = province_clustered_prodi[prov_merge_cols].rename(columns={
                    'Label_Cluster': 'Label_Cluster_Prov',
                    'Cluster': 'Cluster_Prov',
                    'total_score_normalized': 'total_score_prov',
                    **{col: f'Prov_{col}' for col in prov_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    province_clustered_renamed,
                    on='prop_sek',
                    how='left'
                )

                # --- KOTA ---
                city_merge_cols = [col for col in city_clustered_prodi.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                city_merge_cols += ['prop_sek', 'kota_sek', 'total_score_normalized', 'Label_Cluster', 'Cluster']

                city_clustered_renamed = city_clustered_prodi[city_merge_cols].rename(columns={
                    'Label_Cluster': 'Label_Cluster_City',
                    'Cluster': 'Cluster_City',
                    'total_score_normalized': 'total_score_city',
                    **{col: f'City_{col}' for col in city_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    city_clustered_renamed,
                    on=['prop_sek', 'kota_sek'],
                    how='left'
                )

                # --- SEKOLAH ---
                school_merge_cols = [col for col in clustered_data.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                school_merge_cols += ['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi', 'skor_normalized', 'potensi', 'Cluster']

                school_clustered_renamed = clustered_data[school_merge_cols].rename(columns={
                    'Cluster': 'Cluster_School',
                    'potensi': 'Potensi_School',
                    'skor_normalized': 'total_score_school',
                    **{col: f'School_{col}' for col in school_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    school_clustered_renamed,
                    on=['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi'],
                    how='left'
                )


            else:
                filtered_map_data = final_data.copy()
                filtered_map_data['latitude'] = pd.to_numeric(filtered_map_data['latitude'], errors='coerce')
                filtered_map_data['longitude'] = pd.to_numeric(filtered_map_data['longitude'], errors='coerce')
                

                prov_merge_cols = [col for col in province_clustered.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                prov_merge_cols += ['prop_sek', 'total_score_normalized', 'Label_Cluster', 'Cluster']


                province_clustered_renamed = province_clustered[prov_merge_cols].rename(columns={
                    'Label_Cluster': 'Label_Cluster_Prov',
                    'Cluster': 'Cluster_Prov',
                    'total_score_normalized': 'total_score_prov',
                    **{col: f'Prov_{col}' for col in prov_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    province_clustered_renamed,
                    on='prop_sek',
                    how='left'
                )

                # --- KOTA ---
                city_merge_cols = [col for col in city_clustered.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                city_merge_cols += ['prop_sek', 'kota_sek', 'total_score_normalized', 'Label_Cluster', 'Cluster']

                city_clustered_renamed = city_clustered[city_merge_cols].rename(columns={
                    'Label_Cluster': 'Label_Cluster_City',
                    'Cluster': 'Cluster_City',
                    'total_score_normalized': 'total_score_city',
                    **{col: f'City_{col}' for col in city_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    city_clustered_renamed,
                    on=['prop_sek', 'kota_sek'],
                    how='left'
                )

                # --- SEKOLAH ---
                school_merge_cols = [col for col in final_data.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]
                school_merge_cols += ['prop_sek', 'kota_sek', 'nama_sekolah', 'skor_akhir_normalized', 'potensi', 'Cluster']

                school_clustered_renamed = final_data[school_merge_cols].rename(columns={
                    'Cluster': 'Cluster_School',
                    'potensi': 'Potensi_School',
                    'skor_akhir_normalized': 'total_score_school',
                    **{col: f'School_{col}' for col in school_merge_cols if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')}
                })
                filtered_map_data = filtered_map_data.merge(
                    school_clustered_renamed,
                    on=['prop_sek', 'kota_sek', 'nama_sekolah'],
                    how='left'
                )



            # Buat peta dasar
            m = folium.Map(location=[-7.785719, 110.378328], zoom_start=5, tiles='OpenStreetMap', max_bounds=True, control_scale=True)


            if provinsi_filter == "Non-DIY&JATENG":
                filtered_map_data = filtered_map_data[
                    ~filtered_map_data['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])
                ]
            elif provinsi_filter != "SEMUA PROVINSI":
                filtered_map_data = filtered_map_data[filtered_map_data['prop_sek'] == provinsi_filter]

            if kabupaten_filter != "SEMUA KABUPATEN":
                filtered_map_data = filtered_map_data[filtered_map_data['kota_sek'] == kabupaten_filter]
            if tahun_filter:
                filtered_map_data = filtered_map_data[filtered_map_data['tahun'].isin(tahun_filter)]

            prov_group = (
                filtered_map_data.groupby(['prop_sek', 'Label_Cluster_Prov', 'Cluster_Prov'])
                .agg({
                    'latitude': 'mean',
                    'longitude': 'mean'
                })
                .reset_index()
            )

            provinsi_data = []
            for _, row in prov_group.iterrows():
                info = filtered_map_data[filtered_map_data['prop_sek'] == row['prop_sek']].iloc[0]
                
                centroid_info = ""
                for col in info.index:
                    if col.startswith("Prov_Centroid_"):
                        idx = col.split("_")[-1]
                        jarak_col = f"Prov_Jarak_Centroid_{idx}"
                        centroid_info += f"Centroid {idx}: {info[col]:.2f}<br>"
                        if jarak_col in info:
                            centroid_info += f"Jarak ke Centroid {idx}: {info[jarak_col]:.2f}<br>"



                popup = f"""
                    <b>Provinsi: {row['prop_sek']}</b><br>
                    Total Score Provinsi: {info['total_score_prov']:.2f}<br>
                    {centroid_info}
                    Cluster: {row['Cluster_Prov']}<br>
                    Label: {row['Label_Cluster_Prov']}<br>
                """


                provinsi_data.append({
                    "lat": row["latitude"],
                    "lon": row["longitude"],
                    "popup": popup,
                    "color": get_cluster_color(row['Label_Cluster_Prov'])
                })


            kota_group = (
                filtered_map_data.groupby(['kota_sek', 'Label_Cluster_City', 'Cluster_City'])
                .agg({
                    'latitude': 'mean',
                    'longitude': 'mean',
                    'prop_sek': 'first'
                })
                .reset_index()
            )


            kota_data = []
            for _, row in kota_group.iterrows():
                info = filtered_map_data[filtered_map_data['kota_sek'] == row['kota_sek']].iloc[0]
                centroid_info = ""
                for col in info.index:
                    if col.startswith("City_Centroid_"):
                        idx = col.split("_")[-1]
                        jarak_col = f"City_Jarak_Centroid_{idx}"
                        centroid_info += f"Centroid {idx}: {info[col]:.2f}<br>"
                        if jarak_col in info:
                            centroid_info += f"Jarak ke Centroid {idx}: {info[jarak_col]:.2f}<br>"


                popup = f"""
                    <b>Kota: {row['kota_sek']}, {row['prop_sek']}</b><br>
                    Total Score Kota: {info['total_score_city']:.2f}<br>
                    {centroid_info}
                    Cluster: {int(row['Cluster_City'])}<br>
                    Label: {row['Label_Cluster_City']}<br>
                """

                kota_data.append({
                    "lat": row["latitude"],
                    "lon": row["longitude"],
                    "popup": popup,
                    "color": get_cluster_color(row['Label_Cluster_City'])
                })

            # --- SEKOLAH ---
            sekolah_data = []
            for _, row in filtered_map_data.iterrows():
                centroid_info = ""
                for col in row.index:
                    if col.startswith("School_Centroid_"):
                        idx = col.split("_")[-1]
                        jarak_col = f"School_Jarak_Centroid_{idx}"
                        centroid_info += f"Centroid {idx}: {row[col]:.2f}<br>"
                        if jarak_col in row:
                            centroid_info += f"Jarak ke Centroid {idx}: {row[jarak_col]:.2f}<br>"

                popup = f"""
                    <b>{row['nama_sekolah']}, {row['kota_sek']}, {row['prop_sek']}</b><br>
                    Total Score: {row['total_score_school']:.2f}<br>
                    {centroid_info}
                    Cluster: {int(row['Cluster_School']) if pd.notnull(row['Cluster_School']) else '-'}<br>
                    Potensi: {row['Potensi_School']}<br>
                """

                sekolah_data.append({
                    "lat": row["latitude"],
                    "lon": row["longitude"],
                    "popup": popup,
                    "color": get_cluster_color(row['Potensi_School'])
                })



            # Convert ke JSON
            provinsi_json = json.dumps(provinsi_data)
            kota_json = json.dumps(kota_data)
            sekolah_json = json.dumps(sekolah_data)

            components.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8" />
                <title>Peta Dinamis</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
                <style>
                    #map {{
                        width: 1095;
                        height: 954px;
                    }}
                    #checkboxContainer {{
                        position: fixed;
                        bottom: 10px;
                        right: 10px;
                        z-index: 1000;
                        background-color: white;
                        padding: 10px;
                        border-radius: 8px;
                        box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
                        max-height: 200px;
                        overflow-y: auto;
                    }}
                </style>
            </head>
            <body>
            <div id="map"></div>

            <div id="checkboxContainer">
                <strong>Filter Label:</strong>
                <div id="labelCheckboxes"></div>
            </div>

            <script>
                const map = L.map('map').setView([-7.79, 110.37], 5);

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 18,
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);

                const provLayer = L.layerGroup();
                const cityLayer = L.layerGroup();
                const schoolLayer = L.layerGroup();

                const provData = {provinsi_json};
                const cityData = {kota_json};
                const schoolData = {sekolah_json};
                const colorMap = {json.dumps({
                    'Paling Potensial': 'green',
                    'Potensial': 'lightgreen',
                    'Cukup Potensial': 'yellow',
                    'Tidak Potensial': 'red',
                    'Sangat Tidak Potensial': 'darkred'
                })};

                function get_cluster_color(label) {{
                    return colorMap[label] || 'gray';
                }}

                const provMarkers = [], cityMarkers = [], schoolMarkers = [];

                provData.forEach(d => {{
                    const marker = L.circle([d.lat, d.lon], {{
                        color: d.color,
                        fillColor: d.color,
                        fillOpacity: 1,
                        radius: 50000
                    }}).bindPopup(d.popup);
                    marker.options.label = d.popup.match(/Label: ([^<]+)/)[1];
                    marker.addTo(provLayer);
                    provMarkers.push(marker);
                }});

                cityData.forEach(d => {{
                    const marker = L.circle([d.lat, d.lon], {{
                        color: d.color,
                        fillColor: d.color,
                        fillOpacity: 1,
                        radius: 20000
                    }}).bindPopup(d.popup);
                    marker.options.label = d.popup.match(/Label: ([^<]+)/)[1];
                    marker.addTo(cityLayer);
                    cityMarkers.push(marker);
                }});

                schoolData.forEach(d => {{
                    const marker = L.circleMarker([d.lat, d.lon], {{
                        color: d.color,
                        fillColor: d.color,
                        fillOpacity: 1,
                        radius: 5
                    }}).bindPopup(d.popup);
                    marker.options.label = d.popup.match(/Potensi: ([^<]+)/)[1];
                    marker.addTo(schoolLayer);
                    schoolMarkers.push(marker);
                }});

                function updateLayers() {{
                    const zoom = map.getZoom();
                    map.removeLayer(provLayer);
                    map.removeLayer(cityLayer);
                    map.removeLayer(schoolLayer);

                    if (zoom <= 5) {{
                        map.addLayer(provLayer);
                        updateCheckboxes(provMarkers);
                    }} else if (zoom === 6) {{
                        map.addLayer(cityLayer);
                        updateCheckboxes(cityMarkers);
                    }} else {{
                        map.addLayer(schoolLayer);
                        updateCheckboxes(schoolMarkers);
                    }}
                }}

                function updateCheckboxes(markers) {{
                    const container = document.getElementById("labelCheckboxes");
                    container.innerHTML = "";
                    const labels = new Set(markers.map(m => m.options.label));

                    labels.forEach(label => {{
                        const id = `chk_${{label.replace(/\\s+/g, '_')}}`;
                        const checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.id = id;
                        checkbox.value = label;
                        checkbox.checked = true;
                        checkbox.onchange = () => applyFilter(markers);

                        const labelEl = document.createElement("label");
                        labelEl.htmlFor = id;
                        labelEl.innerText = " " + label;

                        // Buat bulatan warna
                        const colorSpan = document.createElement("span");
                        colorSpan.style.display = "inline-block";
                        colorSpan.style.width = "12px";
                        colorSpan.style.height = "12px";
                        colorSpan.style.borderRadius = "50%";  // Membuat bulatan
                        colorSpan.style.marginLeft = "10px";  // Memberikan jarak antara label dan bulatan
                        
                        // Ambil warna berdasarkan label
                        const clusterColor = get_cluster_color(label);
                        // Pastikan warna valid, jika tidak beri warna default
                        colorSpan.style.backgroundColor = clusterColor ? clusterColor : "gray";

                        const wrapper = document.createElement("div");
                        wrapper.appendChild(checkbox);
                        wrapper.appendChild(labelEl);
                        wrapper.appendChild(colorSpan);
                        container.appendChild(wrapper);
                    }});

                    applyFilter(markers);
                }}
                

                function applyFilter(markers) {{
                    const checkedValues = Array.from(document.querySelectorAll('#labelCheckboxes input[type="checkbox"]:checked'))
                                            .map(cb => cb.value);

                    markers.forEach(marker => {{
                        if (checkedValues.includes(marker.options.label)) {{
                            marker.addTo(map);
                        }} else {{
                            map.removeLayer(marker);
                        }}
                    }});
                }}

                map.on('zoomend', updateLayers);
                updateLayers();
            </script>
            </body>
            </html>
            """, height=954, scrolling=False)






            

if __name__ == '__main__':
    main()