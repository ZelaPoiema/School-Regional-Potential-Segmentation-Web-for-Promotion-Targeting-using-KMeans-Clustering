import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static, st_folium
import folium
import pandas as pd
from geopy.geocoders import ArcGIS
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import json
import os
import re
import time
from datetime import datetime
from scipy.spatial import ConvexHull, QhullError
from folium.plugins import MarkerCluster
from fuzzywuzzy import process, fuzz
from Levenshtein import distance as levenshtein_distance
import numpy as np
from pathlib import Path
from streamlit_extras.metric_cards import style_metric_cards
from function.nav import Nav
from function.clustering import add_logo
import io
from function.clustering_utils import (
    load_data,
    save_data,
    save,
    iconMetricContainer,
    load_json_files,
    load_rename_references,
    load_coordinates_cache,
    update_coordinates_cache,
    get_coordinates,
    rename_kota_prov,
    clean_data,
    export_to_excel,
    group_and_standardize,
    calculate_weighted_score,
    process_filtered_data,
    categorize_registration_date,
    kmeans_per_region,
    cluster_program_study_by_province,
    kmeans_cluster_program_province,
    cluster_program_study_by_city,
    kmeans_cluster_program_city,
    cluster_by_province,
    kmeans_cluster_province,
    cluster_by_city_in_province,
    kmeans_cluster_city,
    generate_labels_for_clusters,
    hitung_jumlah_cluster_optimal_per_kota,
    hitung_jumlah_cluster_optimal_per_kota_prodi,
    hitung_jumlah_cluster_optimal_kota,
    get_df_hash,

)


st.set_page_config(
    page_title="💠 Clustering PMB UKDW",
    layout="wide"
)
def main():
    # Cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        Nav("clustering")
        st.stop()
    pd.set_option('display.max_columns', None)

    #Display all rows
    pd.set_option('display.max_rows', 500)

    pd.set_option('display.max_columns', None)
    add_logo()

    # Load references
    reference_names = load_json_files()
    # Load reference data for renaming
    rename_references = load_rename_references()
        # Filter Program Studi berdasarkan role dan fakultas
    if 'role' in st.session_state and st.session_state['role'] == 'admisi':
        # Memuat file contoh dari path lokal
        file_contoh = "Data mahasiswa.xlsx"

        # Membuat tombol unduhan untuk file Excel
        with open(file_contoh, "rb") as file:
            st.download_button(
                label="📥 Unduh contoh data",
                data=file,
                file_name="Data_mahasiswa_contoh.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
 


        cleaned_df = load_data()
        # Load coordinates cache when the app is started
        coordinates_cache = load_coordinates_cache()

        # File uploader in the main page area
        uploaded_file = st.file_uploader("Upload your input data file", type=['csv', 'xlsx']) 
        # Handle file upload and data processing if file is uploaded
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                input_df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                input_df = pd.read_excel(uploaded_file)
            # Drop any 'Unnamed' columns
            input_df = input_df.loc[:, ~input_df.columns.str.contains('^Unnamed')]
            # Clean and standardize data
            cleaned_df = clean_data(input_df)  # Clean the data
            cleaned_df = group_and_standardize(cleaned_df, reference_names)  # Standardize school and province names
            # rename kota_sek and prop_sek using the reference data
            cleaned_df = rename_kota_prov(cleaned_df, rename_references)
            # Add registration category
            cleaned_df['Kategori Waktu Pendaftaran'] = cleaned_df['tgl_daftar'].apply(categorize_registration_date)
            # Initialize new columns for latitude and longitude
            cleaned_df['latitude'] = None
            cleaned_df['longitude'] = None
            # Add coordinates to the DataFrame
            for index, row in cleaned_df.iterrows():
                school_name = row['nama_sekolah']
                latitude, longitude = get_coordinates(school_name, coordinates_cache)  # Pass coordinates_cache here
                cleaned_df.at[index, 'latitude'] = latitude
                cleaned_df.at[index, 'longitude'] = longitude
            # Simpan data ke file utama
            save_data(cleaned_df)
            st.cache_data.clear()
            # Muat ulang data gabungan dari file Excel
            cleaned_df = load_data()
            st.success("Data berhasil diunggah dan diperbarui!")
            time.sleep(3)
        Nav("clustering")
    cleaned_df = load_data()
    # Load coordinates cache when the app is started
    coordinates_cache = load_coordinates_cache()
    def render_table_with_pagination_prodi(data, columns, jumlah_cluster_provinsi, jumlah_cluster_kota, jumlah_cluster):
        """
        Menampilkan tabel clustering program studi dengan pagination, dropdown filter, 
        dan opsi export data ke Excel.
        """
        # Baru di sini kita aman akses filtered_schools
        col_export, col2, col3, col4, col5 = st.columns([2, 8, 2, 2, 2])

        if st.session_state.role == "admisi":
            with col2:
                if st.button("🗑 Hapus Semua Data", key="delete_all_prodi", help="Delete All Data"):
                    empty_data = pd.DataFrame()
                    save(empty_data)
                    st.success("Semua data berhasil dihapus!")
                    time.sleep(3)
                    st.rerun()
         # 1️⃣ **Ambil daftar unik dari Cluster_Prov sebagai opsi filter potensi awal**
        # **Ambil daftar unik dari Cluster_Prov, Cluster_City, dan potensi sebagai opsi filter**
        all_potensi_prov_options = ["Semua"] + sorted(final_result_cleaned["Label_Cluster_Prov"].unique(), reverse=True)
        all_potensi_city_options = ["Semua"] + sorted(final_result_cleaned["Label_Cluster_City"].unique(), reverse=True)
        all_potensi_school_options = ["Semua"] + sorted(final_result_cleaned["potensi"].unique(), reverse=True)


        # 1️⃣ **Filter Wilayah Awal (Provinsi & Kabupaten)**
        filtered_data = final_result_cleaned.copy()
        if program_studi_filter and program_studi_filter != "Tidak Ada":     
            # Filter data untuk program studi yang dipilih
            filtered_data = filtered_data[filtered_data['program_studi'] == program_studi_filter]

        if provinsi_filter == "Non-DIY&JATENG":
            filtered_data = filtered_data[
                ~filtered_data['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])
            ]
        elif provinsi_filter != "SEMUA PROVINSI":
            filtered_data = filtered_data[filtered_data['prop_sek'] == provinsi_filter].copy()
        

        if kabupaten_filter != "SEMUA KABUPATEN":
            filtered_data = filtered_data[filtered_data['kota_sek'] == kabupaten_filter].copy()  # Salinan lagi

        if tahun_filter:
            filtered_data = filtered_data[filtered_data['tahun'].isin(tahun_filter)].copy()  # Salinan lagi

        # 2️⃣ **Filter TINGKAT PERTAMA: POTENSI PROVINSI (HANYA Berdasarkan Cluster_Prov)**
        with col3:
            selected_potensi_prov = st.selectbox("Filter Potensi Provinsi:", all_potensi_prov_options, key="filter_potensi_prov")

        # 🚀 Perbaikan: Terapkan hasil filter potensi provinsi KE filtered_prov
        if selected_potensi_prov != "Semua":
            filtered_prov = filtered_data[filtered_data["Label_Cluster_Prov"] == selected_potensi_prov]
        else:
            filtered_prov = filtered_data  # Jika "Semua", gunakan data awal
        
        original_city_count = filtered_prov['kota_sek'].nunique()

        # 3️⃣ **Filter TINGKAT KEDUA: POTENSI KOTA (Berdasarkan Cluster_City)**
        with col4:
            selected_potensi_city = st.selectbox("Filter Potensi Kota:", all_potensi_city_options, key="filter_potensi_city")

        # Ambil kota dengan jumlah unik hanya 1
        single_city_df = filtered_prov if filtered_prov['kota_sek'].nunique() == 1 else pd.DataFrame()

        # 🚀 Terapkan filter normal, tetapi tetap simpan kota tunggal
        if selected_potensi_city != "Semua":
            filtered_city = filtered_prov[filtered_prov["Label_Cluster_City"] == selected_potensi_city]
        else:
            filtered_city = filtered_prov  # Jika "Semua", gunakan hasil filter provinsi saja

        # 🔥 Gabungkan kembali kota tunggal (agar tidak hilang)
        filtered_city = pd.concat([filtered_city, single_city_df], ignore_index=True).drop_duplicates()


        # Group berdasarkan 'Pilihan 1', 'Pilihan 2', 'Cluster', dan informasi lain yang relevan
        grouped_data = filtered_city.groupby(['prop_sek', 'kota_sek', 'nama_sekolah', 'program_studi'], as_index=False).sum()


        # 5️⃣ **Filter TINGKAT KETIGA: POTENSI SEKOLAH (Berdasarkan potensi)**
        with col5:
            selected_potensi_school = st.selectbox("Filter Potensi Sekolah:", all_potensi_school_options, key="filter_potensi_school")

        # 🚀 Perbaikan: Terapkan filter sekolah setelah data di-groupby
        if selected_potensi_school != "Semua":
            filtered_schools = grouped_data[grouped_data["potensi"] == selected_potensi_school]
        else:
            filtered_schools = grouped_data  # Jika "Semua", gunakan hasil groupby
            
        with col_export:
            if not filtered_schools.empty:
                excel_data = export_to_excel(filtered_schools)
                st.download_button(
                    label="📥 Export Data",
                    data=excel_data,
                    file_name="exported_clustering_prodi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # 6️⃣ **Group Provinsi dengan Kota yang Sesuai**
        grouped_provinsi = filtered_prov.groupby(['prop_sek'], as_index=False).agg({
            'total_score_prov': 'max',
            'kota_sek': lambda x: sorted(
                # Pastikan kota yang masuk hanya yang lolos filter
                [k for k in x.unique() if k in filtered_city['kota_sek'].values],
                key=lambda k: -grouped_data.loc[grouped_data['kota_sek'] == k, 'total_score_city'].max()
                if k in grouped_data['kota_sek'].values else 0
            )
        }).sort_values(by=['total_score_prov'], ascending=[False])


        # Mapping nama kolom agar lebih mudah dipahami
        column_label_map = {
            "prop_sek": "Provinsi",
            "kota_sek": "Kota",
            "nama_sekolah": "Nama Sekolah",
            "jumlah_choice1": "Pilihan 1",
            "jumlah_choice2": "Pilihan 2",
            "jumlah_terima": "Total diterima",
            "jumlah_registrasi": "Total Registrasi",
            "skor_normalized": "Skor Normalisasi",
            "Cluster": "Cluster"
        }
        
        # Kolom header
        colms = st.columns([2, 1.7, 1.7, 1, 1, 1, 1, 1] + [1] * jumlah_cluster + [1])
        columns_with_centroids = columns + [f'Jarak_Centroid_{i}' for i in range(jumlah_cluster)] + ["Cluster"]

        
        for col, label in zip(colms, columns_with_centroids):
            col.write(f"**{column_label_map.get(label, label)}**")
        
        # Loop untuk menampilkan provinsi unik dengan dropdown kota dan sekolah
        for idx, row in grouped_provinsi.iterrows():

            # Menentukan jumlah kolom yang diperlukan
            total_cols = 8 + jumlah_cluster + 1  # 9 kolom tetap + jumlah centroid + cluster

            # Menentukan proporsi ukuran kolom
            col_sizes = [1.5, 2, 2, 1, 1, 1, 1, 1] + [1] * jumlah_cluster + [1]

            # Pastikan jumlah elemen di col_sizes sesuai total_cols
            if len(col_sizes) != total_cols:
                col_sizes = col_sizes[:total_cols]  # Potong jika kelebihan
                col_sizes += [1] * (total_cols - len(col_sizes))  # Tambahkan jika kurang

            # Buat kolom dengan ukuran yang sudah ditentukan
            cols = st.columns(col_sizes)

            
            with cols[0]:
                st.write(row['prop_sek'])
            

            with cols[1]:
                # Menampilkan caption jika jumlah kota dalam data asli kurang dari jumlah cluster

                # Ensure selected_kota is set to kabupaten selected in the sidebar
                if kabupaten_filter != "SEMUA KABUPATEN":
                    # If kabupaten_filter is applied, set default value as the selected kabupaten
                    selected_kota = st.selectbox(
                        "",
                        options=row['kota_sek'],
                        key=f"kota_{idx}",
                        index=row['kota_sek'].index(kabupaten_filter) if kabupaten_filter in row['kota_sek'] else 0
                    )
                else:
                     # Menentukan opsi dropdown
                    kota_options = ["Pilih Kota Sekolah"] + row['kota_sek'] if row['kota_sek'] else ["Pilih Kota Sekolah"]

                    # Menampilkan dropdown kota
                    selected_kota = st.selectbox(
                        "",
                        options=kota_options,
                        key=f"kota_{idx}",
                        index=0
                    )
            # Mengambil data kota yang belum terpengaruh filter
            # Ambil jumlah kota dari data sebelum filter untuk memastikan nilai aslinya
            original_city_count = grouped_data[grouped_data['prop_sek'] == row['prop_sek']]['kota_sek'].nunique()
            provinsi = row['prop_sek']  # Nama provinsi
            kota = row['kota_sek']  # Nama provinsi
            # Ambil data filtered_prov untuk kota yang belum terfilter
            filtered_kota = filtered_prov[filtered_prov['prop_sek'] == row['prop_sek']]['kota_sek'].unique()
            # Pastikan hanya mengambil label dari provinsi yang sedang diproses
            label = filtered_prov[filtered_prov['prop_sek'] == row['prop_sek']]['Label_Cluster_City'].dropna().unique()

            # Hapus spasi kosong dan ambil hanya label unik
            label = list(set(lbl.strip() for lbl in label if lbl.strip()))

            # Gabungkan label menjadi string, atau beri pesan default jika kosong
            label = ', '.join(label) if label else "Label tidak tersedia"
            if kabupaten_filter == "SEMUA KABUPATEN":
                # Hitung jumlah cluster optimal untuk seluruh provinsi
                cluster_optimal_kota = hitung_jumlah_cluster_optimal_kota(filtered_city)

                # Ambil info cluster optimal di level provinsi (bukan kota)
                info_opt_prov = cluster_optimal_kota[cluster_optimal_kota['prop_sek'] == row['prop_sek']]
                if original_city_count >= jumlah_cluster_kota and selected_potensi_city == "Semua":
                    if not info_opt_prov.empty:
                        n_optimal_kota = info_opt_prov['jumlah_cluster_optimal'].values[0]
                        score_opt_kota = info_opt_prov['skor_silhouette'].values[0]

                        if score_opt_kota is not None:
                            if jumlah_cluster_kota == n_optimal_kota:
                                st.success("✅ Jumlah cluster yang dipilih untuk kota sudah *sesuai* dengan jumlah cluster optimal berdasarkan analisis silhouette.")
                            else:
                                st.info(f"Jumlah cluster optimal untuk kota di {provinsi} adalah {n_optimal_kota} berdasarkan skor silhouette yang paling tinggi")
                        else:
                            st.info(f"Jumlah data sekolah di kota {selected_kota} terlalu sedikit untuk menghitung jumlah cluster optimal secara valid. Jumlah sekolah: {original_school_count}.")

                # Menampilkan caption jika jumlah kota kurang dari jumlah cluster
                if original_city_count < jumlah_cluster_kota and selected_potensi_city == "Semua":
                    if not info_opt_prov.empty:
                        n_optimal_kota = info_opt_prov['jumlah_cluster_optimal'].values[0]
                        score_opt_kota = info_opt_prov['skor_silhouette'].values[0]
                    if original_city_count == 1:
                        st.info(f"Jumlah kota yang ada di {provinsi} hanya {original_city_count}. K-means Clustering tidak dilakukan pada {kota}")
                    else:
                        st.info(f"Jumlah kota yang ada di {provinsi} < jumlah cluster. Jumlah cluster optimal untuk kota di {provinsi} adalah {n_optimal_kota} berdasarkan skor silhouette tertinggi.")

                # Menampilkan caption jika tidak ada kota yang tersedia dalam dropdown selain 'Pilih Kota Sekolah'
                if len(kota_options) == 1 and selected_potensi_city != "Semua":
                    if original_city_count == 1:
                        st.info(f"Tidak ada kota dengan label potensi sesuai filter karena kota hanya ada 1, sehingga {filtered_kota} hanya memiliki label {label}.")
                    else: 
                        st.info(f"Tidak ada kota dengan label potensi sesuai yang difilter karena kota {filtered_kota} memiliki karakteristik yang sama, sehingga hanya ada satu pusat cluster (centroid) yang terbentuk yaitu cluster {label}.")

            if selected_kota == "Pilih Kota Sekolah":
                sekolah_options = []
            else:
                sekolah_options = filtered_schools[filtered_schools['kota_sek'] == selected_kota]
                sekolah_options = sekolah_options.sort_values(
                    by=['total_score_city', 'skor_normalized'], 
                    ascending=[False, False]
                )
                sekolah_options = list(sekolah_options['nama_sekolah'].unique())

            with cols[2]:
                school_selectbox_options = ["Pilih Nama Sekolah"] + sekolah_options
                selected_sekolah = st.selectbox(
                    "",
                    options=school_selectbox_options,
                    key=f"sekolah_{idx}"
                )
            # =================== Logika Tambahan untuk Level Sekolah ===================ons)
            original_school_count = len(school_selectbox_options) - 1
            sekolah_per_kota = filtered_city[filtered_city['kota_sek'] == selected_kota]['nama_sekolah'].unique().tolist()
            jumlah_sekolah_per_kota = len(sekolah_per_kota)
            # Ambil daftar nama kota dari filtered_city
            filtered_kota = filtered_city['kota_sek'].unique()


            df_cluster_optimal = hitung_jumlah_cluster_optimal_per_kota_prodi(filtered_schools)

            if selected_kota != "Pilih Kota Sekolah" and jumlah_sekolah_per_kota >= jumlah_cluster and selected_potensi_school == "Semua":
                info_kota = df_cluster_optimal[df_cluster_optimal['kota_sek'] == selected_kota]
                if not info_kota.empty:
                    n_optimal = info_kota['jumlah_cluster_optimal'].values[0]
                    score_optimal = info_kota['skor_silhouette'].values[0]

                    if score_optimal is not None:
                        if jumlah_cluster == n_optimal:
                            st.success("✅ Jumlah cluster yang dipilih untuk sekolah sudah *sesuai* dengan jumlah cluster optimal berdasarkan analisis silhouette.")
                        else:
                            st.info(f"Jumlah cluster optimal untuk sekolah di kota {selected_kota} adalah {n_optimal} berdasarkan skor silhouette yang paling tinggi")
                    else:
                        st.info(f"Jumlah data sekolah di kota {selected_kota} terlalu sedikit untuk menghitung jumlah cluster optimal secara valid. Jumlah sekolah: {jumlah_sekolah_per_kota}.")


            if selected_kota != "Pilih Kota Sekolah" and jumlah_sekolah_per_kota < jumlah_cluster and selected_potensi_school == "Semua":
                info_kota = df_cluster_optimal[df_cluster_optimal['kota_sek'] == selected_kota]
                if not info_kota.empty:
                    n_optimal = info_kota['jumlah_cluster_optimal'].values[0]
                    score_optimal = info_kota['skor_silhouette'].values[0]
                    if jumlah_sekolah_per_kota == 1:
                        st.info(f"Hanya terdapat 1 sekolah di kota {selected_kota}, sehingga clustering sekolah tidak dilakukan.")
                    else:
                        if score_optimal is not None:
                            st.info(f"Jumlah sekolah di kota {selected_kota} < ({jumlah_cluster}). Jumlah cluster optimal untuk sekolah di kota {selected_kota} adalah {n_optimal}.")
                        else:
                            st.info(f"Jumlah sekolah di kota {selected_kota} < ({jumlah_cluster}). Data terlalu sedikit untuk menentukan jumlah cluster optimal secara valid.")
            

            # Ambil label potensi sekolah dari filtered_schools berdasarkan nama sekolah yang ada di kota tersebut
            school_labels = filtered_schools[
                filtered_schools['nama_sekolah'].isin(sekolah_per_kota)
            ]['potensi'].dropna().unique()

            # Bersihkan label dari spasi dan pastikan unik
            school_labels = list(set(lbl.strip() for lbl in school_labels if lbl.strip()))
            school_labels = ', '.join(school_labels) if school_labels else "Label tidak tersedia"
            # Menampilkan caption jika tidak ada kota yang tersedia dalam dropdown selain 'Pilih Kota Sekolah'
            if selected_kota != "Pilih Kota Sekolah" and len(school_selectbox_options) == 1 and selected_potensi_school != "Semua":
                if jumlah_sekolah_per_kota == 1:
                    st.info(f"Tidak ada sekolah dengan label potensi sesuai filter karena sekolah hanya ada 1, sehingga {sekolah_per_kota} tidak bisa dilakukan clustering dan tidak memiliki label")
                else: 
                    st.info(f"Tidak ada sekolah dengan label potensi sesuai yang difilter karena sekolah {sekolah_per_kota} memiliki karakteristik yang sama, sehingga hanya ada satu pusat cluster (centroid) yang terbentuk yaitu cluster {school_labels}.")

            # Variables for storing summed data
            jumlah_choice1, jumlah_choice2, jumlah_terima, jumlah_registrasi = 0, 0, 0, 0
            skor_normalized, cluster = 0, 0
            centroid_distances = [0] * jumlah_cluster  # List to store distance for each centroid
            if selected_sekolah != "Pilih Nama Sekolah":
                selected_data = grouped_data[
                    (grouped_data['prop_sek'] == row['prop_sek']) &
                    (grouped_data['kota_sek'] == selected_kota) &
                    (grouped_data['nama_sekolah'] == selected_sekolah)
                ]
                jumlah_choice1 = selected_data['jumlah_choice1'].sum()
                jumlah_choice2 = selected_data['jumlah_choice2'].sum()
                jumlah_terima = selected_data['jumlah_terima'].sum()
                jumlah_registrasi = selected_data['jumlah_registrasi'].sum()
                skor_normalized = round(selected_data['skor_normalized'].sum(), 2)
                cluster = selected_data['Cluster'].iloc[0]  # Ambil nilai pertama dari Cluster

                # Dynamically fill the centroid distances
                for i in range(jumlah_cluster):
                    centroid_distances[i] = round(selected_data[f'Jarak_Centroid_{i}'].sum(), 2)
            else:
                centroid_distances = [0] * jumlah_cluster  # Reset if no school selected

            with cols[3]: st.write(jumlah_choice1)
            with cols[4]: st.write(jumlah_choice2)
            with cols[5]: st.write(jumlah_terima)
            with cols[6]: st.write(jumlah_registrasi)
            with cols[7]: st.write(f"{skor_normalized:.2f}")
            
             # Menampilkan jarak centroid pada kolom dinamis
            for i in range(jumlah_cluster):
                with cols[8 + i]:  # Dimulai dari indeks 9
                    st.write(f"{centroid_distances[i]:.2f}")

            # Menampilkan kolom cluster di akhir
            with cols[8 + jumlah_cluster]:  # Kolom setelah centroid
                st.write(int(cluster))


    # Fungsi untuk menampilkan tabel dengan pagination dan dropdown
    def render_table_with_pagination(data, columns, jumlah_cluster_provinsi, jumlah_cluster_kota, jumlah_cluster):
        """
        Menampilkan tabel dengan pagination, pilihan jumlah baris yang ditampilkan,
        serta fitur untuk menghapus semua data dan dropdown di dalam tabel.
        """
        # Baru di sini kita aman akses filtered_schools
        col_export, col2, col3, col4, col5 = st.columns([2, 8, 2, 2, 2])

        if st.session_state.role == "admisi":
            with col2:
                if st.button("🗑 Hapus Semua Data", key="delete_all", help="Delete All Data"):
                    # Hapus semua data yang ada dengan menyimpan DataFrame kosong
                    empty_data = pd.DataFrame()  # DataFrame kosong
                    save(empty_data)  # Fungsi save untuk menyimpan perubahan
                    st.success("Semua data berhasil dihapus!")
                    st.rerun()
        
        # 1️⃣ **Ambil daftar unik dari Cluster_Prov sebagai opsi filter potensi awal**
        all_potensi_prov_options = ["Semua"] + sorted(final_result_cleaned["Label_Cluster_Prov"].unique(), reverse=True)
        all_potensi_city_options = ["Semua"] + sorted(final_result_cleaned["Label_Cluster_City"].unique(), reverse=True)
        all_potensi_school_options = ["Semua"] + sorted(final_result_cleaned["potensi"].unique(), reverse=True)

        # **Filter Awal Berdasarkan Provinsi dan Kabupaten**
        filtered_data = final_result_cleaned.copy()
        if provinsi_filter == "Non-DIY&JATENG":
            filtered_data = filtered_data[
                ~filtered_data['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])
            ]
        elif provinsi_filter != "SEMUA PROVINSI":
            filtered_data = filtered_data[filtered_data['prop_sek'] == provinsi_filter]

        if kabupaten_filter != "SEMUA KABUPATEN":
            filtered_data = filtered_data[filtered_data['kota_sek'] == kabupaten_filter]
        
        # 2️⃣ **Filter TINGKAT PERTAMA: POTENSI PROVINSI (HANYA Berdasarkan Cluster_Prov)**
        with col3:
            selected_potensi_prov = st.selectbox("Filter Potensi Provinsi:", all_potensi_prov_options, key="filter_potensi_prov")

         # 🚀 Perbaikan: Terapkan hasil filter potensi provinsi KE filtered_prov
        if selected_potensi_prov != "Semua":
            filtered_prov = filtered_data[filtered_data["Label_Cluster_Prov"] == selected_potensi_prov]
        else:
            filtered_prov = filtered_data  # Jika "Semua", gunakan data awal
        
        original_city_count = filtered_prov['kota_sek'].nunique()

        # 3️⃣ **Filter TINGKAT KEDUA: POTENSI KOTA (Berdasarkan Cluster_City)**
        with col4:
            selected_potensi_city = st.selectbox("Filter Potensi Kota:", all_potensi_city_options, key="filter_potensi_city")

        # Ambil kota dengan jumlah unik hanya 1
        single_city_df = filtered_prov if filtered_prov['kota_sek'].nunique() == 1 else pd.DataFrame()

        # 🚀 Terapkan filter normal, tetapi tetap simpan kota tunggal
        if selected_potensi_city != "Semua":
            filtered_city = filtered_prov[filtered_prov["Label_Cluster_City"] == selected_potensi_city]
        else:
            filtered_city = filtered_prov  # Jika "Semua", gunakan hasil filter provinsi saja
         # 5️⃣ **Filter TINGKAT KETIGA: POTENSI SEKOLAH (Berdasarkan potensi)**
        grouped_data = filtered_city.groupby(['prop_sek', 'kota_sek', 'nama_sekolah'], as_index=False).sum().reset_index()
        with col5:
            selected_potensi_school = st.selectbox("Filter Potensi Sekolah:", all_potensi_school_options, key="filter_potensi_school")

        # 🚀 Perbaikan: Terapkan filter sekolah setelah data di-groupby
        if selected_potensi_school != "Semua":
            filtered_schools = grouped_data[grouped_data["potensi"] == selected_potensi_school]
        else:
            filtered_schools = grouped_data  # Jika "Semua", gunakan hasil groupby

        with col_export:
            if not filtered_schools.empty:
                excel_data = export_to_excel(filtered_schools)
                st.download_button(
                    label="📥 Export Data",
                    data=excel_data,
                    file_name="exported_clustering.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        grouped_provinsi = filtered_prov.groupby('prop_sek', as_index=False).agg({
            'total_score_prov': 'max',
            'kota_sek': lambda x: sorted(
                # Pastikan kota yang masuk hanya yang lolos filter
                [k for k in x.unique() if k in filtered_city['kota_sek'].values],
                key=lambda k: -grouped_data.loc[grouped_data['kota_sek'] == k, 'total_score_city'].max()
                if k in grouped_data['kota_sek'].values else 0
            )
        }).sort_values(by=['total_score_prov'], ascending=[False])

        # Mapping nama kolom ke label tampilan
        column_label_map = {
            "prop_sek": "Provinsi",
            "kota_sek": "Kota",
            "nama_sekolah": "Nama Sekolah",
            "total_pendaftar": "Total Pendaftar",
            "total_lulus": "Total Lulus",
            "total_regist": "Total Registrasi",
            "total_batal": "Total Batal",
            "bobot_waktu": "Skor Waktu Pendaftaran",
            "skor_akhir": "Skor Akhir",
            "skor_akhir_normalized": "Skor Normalisasi",
            "Cluster": "Cluster"
        }

        # Kolom header
        colms = st.columns([2, 1.7, 1.3, 1, 1, 1, 1, 1, 1, 1] + [1] * jumlah_cluster + [1])

        # Tambahkan kolom centroid dan cluster
        columns_with_centroids = columns + [f'Jarak_Centroid_{i}' for i in range(jumlah_cluster)] + ["Cluster"]

        # Menampilkan header tabel dengan label yang benar
        for col, label in zip(colms, columns_with_centroids):
            col.write(f"**{column_label_map.get(label, label)}**")  # Ganti nama sesuai mapping

        # Loop untuk menampilkan provinsi unik dengan dropdown kota dan sekolah
        for idx, row in grouped_provinsi.iterrows():
            # Menentukan jumlah kolom yang diperlukan
            total_cols = 10 + jumlah_cluster + 1  # 9 kolom tetap + jumlah centroid + cluster

            # Menentukan proporsi ukuran kolom
            col_sizes = [1.5, 2, 2, 1, 1, 1, 1, 1, 1, 1] + [1] * jumlah_cluster + [1]

            # Pastikan jumlah elemen di col_sizes sesuai total_cols
            if len(col_sizes) != total_cols:
                col_sizes = col_sizes[:total_cols]  # Potong jika kelebihan
                col_sizes += [1] * (total_cols - len(col_sizes))  # Tambahkan jika kurang

            # Buat kolom dengan ukuran yang sudah ditentukan
            cols = st.columns(col_sizes)

            
            with cols[0]:
                st.write(row['prop_sek'])

            with cols[1]:
                # Ensure selected_kota is set to kabupaten selected in the sidebar
                if kabupaten_filter != "SEMUA KABUPATEN":
                    # If kabupaten_filter is applied, set default value as the selected kabupaten
                    selected_kota = st.selectbox(
                        "",
                        options=row['kota_sek'],
                        key=f"kota_{idx}",
                        index=row['kota_sek'].index(kabupaten_filter) if kabupaten_filter in row['kota_sek'] else 0
                    )
                else:
                    # Menentukan opsi dropdown
                    kota_options = ["Pilih Kota Sekolah"] + row['kota_sek'] if row['kota_sek'] else ["Pilih Kota Sekolah"]

                    # Menampilkan dropdown kota
                    selected_kota = st.selectbox(
                        "",
                        options=kota_options,
                        key=f"kota_{idx}",
                        index=0
                    )

            # Mengambil data kota yang belum terpengaruh filter
            # Ambil jumlah kota dari data sebelum filter untuk memastikan nilai aslinya
            original_city_count = grouped_data[grouped_data['prop_sek'] == row['prop_sek']]['kota_sek'].nunique()
            provinsi = row['prop_sek']  # Nama provinsi
            kota = row['kota_sek']  # Nama provinsi
            # Ambil data filtered_prov untuk kota yang belum terfilter
            filtered_kota = filtered_prov[filtered_prov['prop_sek'] == row['prop_sek']]['kota_sek'].unique()
            # Pastikan hanya mengambil label dari provinsi yang sedang diproses
            label = filtered_prov[filtered_prov['prop_sek'] == row['prop_sek']]['Label_Cluster_City'].dropna().unique()

            # Hapus spasi kosong dan ambil hanya label unik
            label = list(set(lbl.strip() for lbl in label if lbl.strip()))

            # Gabungkan label menjadi string, atau beri pesan default jika kosong
            label = ', '.join(label) if label else "Label tidak tersedia"
            if kabupaten_filter == "SEMUA KABUPATEN":
                # Hitung jumlah cluster optimal untuk seluruh provinsi
                cluster_optimal_kota = hitung_jumlah_cluster_optimal_kota(filtered_city)
                # Ambil info cluster optimal di level provinsi (bukan kota)
                info_opt_prov = cluster_optimal_kota[cluster_optimal_kota['prop_sek'] == row['prop_sek']]
                if original_city_count >= jumlah_cluster_kota and selected_potensi_city == "Semua":
                    if not info_opt_prov.empty:
                        n_optimal_kota = info_opt_prov['jumlah_cluster_optimal'].values[0]
                        score_opt_kota = info_opt_prov['skor_silhouette'].values[0]

                        if score_opt_kota is not None:
                            if jumlah_cluster_kota == n_optimal_kota:
                                st.success(f"✅ Jumlah cluster untuk kota yang dipilih sudah *sesuai* dengan jumlah cluster optimal berdasarkan analisis silhouette")
                            else:
                                st.info(f"Jumlah cluster optimal untuk kota di {provinsi} adalah {n_optimal_kota} berdasarkan skor silhouette yang paling tinggi")
                        else:
                            st.info(f"Jumlah data sekolah di kota {selected_kota} terlalu sedikit untuk menghitung jumlah cluster optimal secara valid. Jumlah sekolah: {original_school_count}.")

                # Menampilkan caption jika jumlah kota kurang dari jumlah cluster
                if original_city_count < jumlah_cluster_kota and selected_potensi_city == "Semua":
                    if not info_opt_prov.empty:
                        n_optimal_kota = info_opt_prov['jumlah_cluster_optimal'].values[0]
                        score_opt_kota = info_opt_prov['skor_silhouette'].values[0]
                    if original_city_count == 1:
                        st.info(f"Jumlah kota yang ada di {provinsi} hanya {original_city_count}. K-means Clustering tidak dilakukan pada {kota}")
                    else:
                        st.info(f"Jumlah kota yang ada di {provinsi} < jumlah cluster. Jumlah cluster optimal untuk kota di {provinsi} adalah {n_optimal_kota} berdasarkan skor silhouette tertinggi.")
                # Menampilkan caption jika tidak ada kota yang tersedia dalam dropdown selain 'Pilih Kota Sekolah'
                if len(kota_options) == 1 and selected_potensi_city != "Semua":
                    if original_city_count == 1:
                        st.info(f"Tidak ada kota dengan label potensi sesuai filter karena kota hanya ada 1, sehingga {filtered_kota} hanya memiliki label {label}.")
                    else: 
                        st.info(f"Tidak ada kota dengan label potensi sesuai yang difilter karena kota {filtered_kota} memiliki karakteristik yang sama, sehingga hanya ada satu pusat cluster (centroid) yang terbentuk yaitu cluster {label}.")
            
            if selected_kota == "Pilih Kota Sekolah":
                sekolah_options = []
            else:
                sekolah_options = filtered_schools[filtered_schools['kota_sek'] == selected_kota]
                sekolah_options = sekolah_options.sort_values(
                    by=['total_score_city', 'skor_akhir'], 
                    ascending=[False, False]
                )
                sekolah_options = list(sekolah_options['nama_sekolah'].unique())
            
            with cols[2]:
                school_selectbox_options = ["Pilih Nama Sekolah"] + sekolah_options
                selected_sekolah = st.selectbox(
                    "",
                    options=school_selectbox_options,
                    key=f"sekolah_{idx}"
                )
            # =================== Logika Tambahan untuk Level Sekolah ===================ons)
            original_school_count = len(school_selectbox_options) - 1
            sekolah_per_kota = filtered_city[filtered_city['kota_sek'] == selected_kota]['nama_sekolah'].unique().tolist()
            jumlah_sekolah_per_kota = len(sekolah_per_kota)
            # Ambil daftar nama kota dari filtered_city
            filtered_kota = filtered_city['kota_sek'].unique()

            df_cluster_optimal = hitung_jumlah_cluster_optimal_per_kota(filtered_schools)

            if selected_kota != "Pilih Kota Sekolah" and jumlah_sekolah_per_kota >= jumlah_cluster and selected_potensi_school == "Semua":
                info_kota = df_cluster_optimal[df_cluster_optimal['kota_sek'] == selected_kota]
                if not info_kota.empty:
                    n_optimal = info_kota['jumlah_cluster_optimal'].values[0]
                    score_optimal = info_kota['skor_silhouette'].values[0]

                    if score_optimal is not None:
                        if jumlah_cluster == n_optimal:
                            st.success("✅ Jumlah cluster yang dipilih untuk sekolah sudah *sesuai* dengan jumlah cluster optimal berdasarkan analisis silhouette.")
                        else:
                            st.info(f"Jumlah cluster optimal untuk sekolah di kota {selected_kota} adalah {n_optimal} berdasarkan skor silhouette yang paling tinggi")
                    else:
                        st.info(f"Jumlah data sekolah di kota {selected_kota} terlalu sedikit untuk menghitung jumlah cluster optimal secara valid. Jumlah sekolah: {jumlah_sekolah_per_kota}.")


            if selected_kota != "Pilih Kota Sekolah" and jumlah_sekolah_per_kota < jumlah_cluster and selected_potensi_school == "Semua":
                info_kota = df_cluster_optimal[df_cluster_optimal['kota_sek'] == selected_kota]
                if not info_kota.empty:
                    n_optimal = info_kota['jumlah_cluster_optimal'].values[0]
                    score_optimal = info_kota['skor_silhouette'].values[0]
                    if jumlah_sekolah_per_kota == 1:
                        st.info(f"Hanya terdapat 1 sekolah di kota {selected_kota}, sehingga clustering sekolah tidak dilakukan.")
                    else:
                        if score_optimal is not None:
                            st.info(f"Jumlah sekolah di kota {selected_kota} < ({jumlah_cluster}). Jumlah cluster optimal untuk sekolah di kota {selected_kota} adalah {n_optimal}.")
                        else:
                            st.info(f"Jumlah sekolah di kota {selected_kota} < ({jumlah_cluster}). Data terlalu sedikit untuk menentukan jumlah cluster optimal secara valid.")
            
               # Ambil label potensi sekolah dari filtered_schools berdasarkan nama sekolah yang ada di kota tersebut
            school_labels = filtered_schools[
                filtered_schools['nama_sekolah'].isin(sekolah_per_kota)
            ]['potensi'].dropna().unique()

            # Bersihkan label dari spasi dan pastikan unik
            school_labels = list(set(lbl.strip() for lbl in school_labels if lbl.strip()))
            school_labels = ', '.join(school_labels) if school_labels else "Label tidak tersedia"
            # Menampilkan caption jika tidak ada kota yang tersedia dalam dropdown selain 'Pilih Kota Sekolah'
            if selected_kota != "Pilih Kota Sekolah" and len(school_selectbox_options) == 1 and selected_potensi_school != "Semua":
                if jumlah_sekolah_per_kota == 1:
                    st.info(f"Tidak ada sekolah dengan label potensi sesuai filter karena sekolah hanya ada 1, sehingga {sekolah_per_kota} hanya memiliki label {school_labels}.")
                else: 
                    st.info(f"Tidak ada sekolah dengan label potensi sesuai yang difilter karena sekolah {sekolah_per_kota} memiliki karakteristik yang sama, sehingga hanya ada satu pusat cluster (centroid) yang terbentuk yaitu cluster {school_labels}.")

            # Variables for storing summed data
            total_pendaftar, total_lulus, total_regist, total_batal, skor_waktu = 0, 0, 0, 0, 0
            skor_akhir, skor_akhir_normalized, cluster = 0, 0, 0
            centroid_distances = [0] * jumlah_cluster  # List to store distance for each centroid

            if selected_sekolah != "Pilih Nama Sekolah":
                selected_data = grouped_data[
                    (grouped_data['prop_sek'] == row['prop_sek']) &
                    (grouped_data['kota_sek'] == selected_kota) &
                    (grouped_data['nama_sekolah'] == selected_sekolah)
                ]
                total_pendaftar = selected_data['total_pendaftar'].sum()
                total_lulus = selected_data['total_lulus'].sum()
                total_regist = selected_data['total_regist'].sum()
                total_batal = selected_data['total_batal'].sum()
                skor_waktu = selected_data['bobot_waktu'].sum()
                skor_akhir = round(selected_data['skor_akhir'].sum(), 2)
                skor_akhir_normalized = round(selected_data['skor_akhir_normalized'].sum(), 2)
                cluster = selected_data['Cluster'].sum()

                # Dynamically fill the centroid distances
                for i in range(jumlah_cluster):
                    centroid_distances[i] = round(selected_data[f'Jarak_Centroid_{i}'].sum(), 2)
            else:
                centroid_distances = [0] * jumlah_cluster  # Reset if no school selected

            # Display the data in corresponding columns
            with cols[3]: st.write(int(total_pendaftar))
            with cols[4]: st.write(int(total_lulus))
            with cols[5]: st.write(int(total_regist))
            with cols[6]: st.write(int(total_batal))
            with cols[7]: st.write(int(skor_waktu))
            with cols[8]: st.write(f"{skor_akhir:.2f}")
            with cols[9]: st.write(f"{skor_akhir_normalized:.2f}")

            # Menampilkan jarak centroid pada kolom dinamis
            for i in range(jumlah_cluster):
                with cols[10 + i]:  # Dimulai dari indeks 9
                    st.write(f"{centroid_distances[i]:.2f}")

            # Menampilkan kolom cluster di akhir
            with cols[10 + jumlah_cluster]:  # Kolom setelah centroid
                st.write(int(cluster))

    if cleaned_df.empty:
        st.error("Data tidak ditemukan. Pastikan data sudah diunggah.")
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

        # Save coordinates cache after processing
        update_coordinates_cache(coordinates_cache)
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
        final_data['potensi'] = 'Potensial'
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
            province_clustered, centroid_values = kmeans_cluster_province(
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
            centroid_values = None
        

        # Sorting provinsi berdasarkan cluster dan skor
        province_clustered = province_clustered.sort_values(
            by=['Label_Cluster', 'total_score_normalized', 'total_score'], ascending=[False, False, False]
        )

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

        # Sorting kota berdasarkan total_score tertinggi dalam provinsi dan Label_Cluster
        city_clustered = city_clustered.sort_values(by=['prop_sek', 'Label_Cluster', 'total_score_normalized', 'total_score'], ascending=[True, False, False, False])
    
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
        clustered_data['potensi'] = 'Potensial'
        for result in iteration_results_prodi:
            if len(result["centroids"]) == 0:
                continue

            centroids = result["centroids"]
            mask = (clustered_data['prop_sek'] == result["provinsi"]) & (clustered_data['kota_sek'] == result["kota"])

            # Tentukan label untuk masing-masing cluster berdasarkan centroid
            centroid_labels = generate_labels_for_clusters(len(centroids), centroids)
            clustered_data.loc[mask, 'potensi'] = clustered_data.loc[mask, 'Cluster'].map(centroid_labels)

        # Clustering dan sorting provinsi berdasarkan centroid dan label
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
            centroid_values = None

        

        # Sorting provinsi berdasarkan total_score dan Label_Cluster
        province_clustered_prodi = province_clustered_prodi.sort_values(by=['Label_Cluster', 'total_score_normalized'], ascending=[False, False])

        # Clustering dan sorting kota dalam provinsi
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

        # Sorting kota berdasarkan total_score tertinggi dalam provinsi dan Label_Cluster
        city_clustered_prodi = city_clustered_prodi.sort_values(by=['prop_sek', 'Label_Cluster', 'total_score_normalized'], ascending=[True, False, False])
        # Display results in the next section
        if cleaned_df is not None:
            if program_studi_filter and program_studi_filter != "Tidak Ada":
                # Filter data untuk program studi yang dipilih
                filtered_clustered_data = clustered_data[clustered_data['program_studi'] == program_studi_filter]
                if provinsi_filter == "Non-DIY&JATENG":
                    filtered_clustered_data = filtered_clustered_data[
                        ~filtered_clustered_data['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])
                    ]
                elif provinsi_filter != "SEMUA PROVINSI":
                    filtered_clustered_data = filtered_clustered_data[filtered_clustered_data['prop_sek'] == provinsi_filter]

                if kabupaten_filter != "SEMUA KABUPATEN":
                    filtered_clustered_data = filtered_clustered_data[filtered_clustered_data['kota_sek'] == kabupaten_filter]
                if tahun_filter:
                    filtered_clustered_data = filtered_clustered_data[filtered_clustered_data['tahun'].isin(tahun_filter)]
                
                # 🎯 Hitung jumlah sekolah unik
                jumlah_sekolah = filtered_clustered_data['nama_sekolah'].nunique()

                # 🎯 Hitung jumlah sekolah per kategori potensi
                cluster_counts_filtered = (
                    filtered_clustered_data.groupby('potensi')['nama_sekolah']
                    .nunique()
                    .to_dict()
                )

               # Pastikan cluster_counts_filtered memiliki kategori potensi meskipun kosong
                if not cluster_counts_filtered:
                    cluster_counts_filtered = {"Tidak Ada": 0}

                # 🎯 Tampilkan hasil dalam Streamlit
                total_cols = len(cluster_counts_filtered) + 4  # +1 untuk total sekolah
                col_sizes = [1] * total_cols  
                cols = st.columns(col_sizes, gap="small")   

                # 🏫 **Total Sekolah**
                with cols[0]:  
                    iconMetricContainer(key="jumlah_sekolah", iconUnicode="\eb2a", color="black")  
                    st.metric(label="Jumlah Sekolah", value=f"{jumlah_sekolah}")

                # 📊 **Card untuk tiap cluster dengan ukuran kolom yang sama**
                for idx, (label, count) in enumerate(cluster_counts_filtered.items(), start=1):
                    with cols[idx]:  
                        iconMetricContainer(key=f"jumlah_{label.lower().replace(' ', '_')}", iconUnicode="\eb2a", color="black")  
                        st.metric(label=f"Sekolah {label}", value=f"{count}")


                final_result_cleaned = filtered_clustered_data[['prop_sek', 'kota_sek', 'nama_sekolah', 'jumlah_choice1',
                                   'jumlah_choice2', 'jumlah_terima', 'jumlah_registrasi', 'skor', 'skor_normalized',
                                   'Cluster', 'potensi', 'tahun', 'program_studi']]
                # Dynamically add columns for each Jarak_Centroid
                for i in range(cluster_sekolah):
                    final_result_cleaned[f'Jarak_Centroid_{i}'] = clustered_data[f'Jarak_Centroid_{i}']

                # Merge provinsi ke dalam tabel utama berdasarkan clustering
                final_result_cleaned = final_result_cleaned.merge(
                    province_clustered_prodi[['prop_sek', 'program_studi', 'total_score', 'total_score_normalized', 'Label_Cluster']],
                    on=['prop_sek', 'program_studi'],
                    how='left'
                ).rename(columns={'total_score': 'total_score_prov', 'total_score_normalized': 'total_score_normalized_prov', 'Label_Cluster': 'Label_Cluster_Prov'})
                
                if centroid_values is not None:
                     # Buat kolom centroid provinsi dan jaraknya di final_data
                    for i in range(cluster_provinsi):
                        final_result_cleaned[f'Centroid_Prov_{i}'] = centroid_values[i]
                        final_result_cleaned[f'Jarak_Centroid_Prov_{i}'] = np.abs(final_result_cleaned['total_score_normalized_prov'] - centroid_values[i])
                else:
                    for i in range(cluster_provinsi):
                        final_result_cleaned[f'Centroid_Prov_{i}'] = 0
                        final_result_cleaned[f'Jarak_Centroid_Prov_{i}'] = 0

                # Merge kota ke dalam tabel utama berdasarkan clustering
                final_result_cleaned = final_result_cleaned.merge(
                    city_clustered_prodi[['prop_sek', 'program_studi', 'kota_sek', 'total_score', 'total_score_normalized', 'Label_Cluster']],
                    on=['prop_sek', 'kota_sek', 'program_studi'],
                    how='left'
                ).rename(columns={'total_score': 'total_score_city', 'total_score_normalized': 'total_score_normalized_city', 'Label_Cluster': 'Label_Cluster_City'})

                # Sorting berdasarkan total_score_prov dan total_score_city
                final_result_cleaned = final_result_cleaned.sort_values(
                    by=['total_score_prov', 'total_score_city', 'skor_normalized'],
                    ascending=[False, False, False]
                )

                # 6. Tampilkan tabel dengan hasil yang sudah diurutkan
                if not final_result_cleaned.empty:
                    columns = [
                        ("prop_sek", "Provinsi"),
                        ("kota_sek", "Kota Sekolah"),
                        ("nama_sekolah", "Nama Sekolah"),
                        ("jumlah_choice1", "Pilihan 1"),
                        ("jumlah_choice2", "Pilihan 2"),
                        ("jumlah_terima", "Diterima"),
                        ("jumlah_registrasi", "Registrasi"),
                        ("skor", "Skor Akhir"),
                        ("skor_normalized", "Skor Normalisasi"),
                    ]
                    
                    # Dynamically add 'Jarak_Centroid_X' columns based on number of clusters
                    for i in range(cluster_sekolah):
                        columns.append((f'Jarak_Centroid_{i}', f'Jarak ke Centroid {i}'))

                    # Add "Cluster" column after the centroid columns
                    columns.append(("Cluster", "Cluster"))
                    column_names = [col[0] for col in columns]  # Ambil hanya nama kolomnya
                    render_table_with_pagination_prodi(final_result_cleaned, column_names, cluster_provinsi, cluster_kota, cluster_sekolah)
                else:
                    st.warning(f"Tidak ada data untuk program studi: {program_studi_filter}")
            else:


                # 🎯 Hitung jumlah total sekolah
                final_result_cleaned = final_data[['prop_sek', 'kota_sek', 'nama_sekolah', 'total_pendaftar',
                                   'total_lulus', 'total_regist', 'total_batal', 'bobot_waktu', 'skor_akhir',
                                   'skor_akhir_normalized', 'Cluster', 'potensi', 'tahun']]
                  # 4. Normalisasi Nama Provinsi sebelum Filtering
                final_result_cleaned['prop_sek'] = final_result_cleaned['prop_sek'].str.strip().str.upper()

                if provinsi_filter == "Non-DIY&JATENG":
                    final_result_cleaned = final_result_cleaned[
                        ~final_result_cleaned['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])
                    ]
                elif provinsi_filter != "SEMUA PROVINSI":
                    final_result_cleaned = final_result_cleaned[final_result_cleaned['prop_sek'] == provinsi_filter]


                # Filter berdasarkan kabupaten jika ada yang dipilih
                if kabupaten_filter != "SEMUA KABUPATEN":
                    final_result_cleaned = final_result_cleaned[final_result_cleaned['kota_sek'] == kabupaten_filter]

                if tahun_filter:
                    final_result_cleaned = final_result_cleaned[final_result_cleaned['tahun'].isin(tahun_filter)]
                # 🎯 Hitung jumlah sekolah unik dengan groupby, sesuai default saat "Tidak Ada"
                grouped_sekolah = final_result_cleaned.groupby(['nama_sekolah', 'prop_sek', 'kota_sek']).size().reset_index()
                jumlah_sekolah = len(grouped_sekolah)

                # 🎯 Dapatkan label cluster dari fungsi generate_labels_for_clusters()
                centroid_labels = generate_labels_for_clusters(cluster_sekolah, centroids)

                # 🎯 Hitung jumlah sekolah per label cluster
                cluster_counts = {label: 0 for label in centroid_labels.values()}  # Inisialisasi

                for label in cluster_counts.keys():
                    cluster_counts[label] = len(grouped_sekolah[grouped_sekolah['nama_sekolah'].isin(final_result_cleaned[final_result_cleaned['potensi'] == label]['nama_sekolah'])])

                # 🎯 Tentukan jumlah kolom (lebih 1 dari jumlah card)
                total_cols = len(cluster_counts) + 4  # +1 untuk total sekolah, +1 tambahan spasi

                # 🎯 Buat list ukuran kolom
                col_sizes = [1] * total_cols  

                # 🎯 Inisialisasi kolom dengan ukuran yang menyesuaikan jumlah card
                cols = st.columns(col_sizes, gap="small")   

                # 🏫 **Total Sekolah**
                with cols[0]:  
                    iconMetricContainer(key="jumlah_sekolah", iconUnicode="\eb2a", color="black")  
                    st.metric(label="Jumlah Sekolah", value=f"{jumlah_sekolah}")

                # 📊 **Card untuk tiap cluster dengan ukuran kolom yang sama**
                for idx, (label, count) in enumerate(cluster_counts.items(), start=1):
                    with cols[idx]:  
                        iconMetricContainer(key=f"jumlah_{label.lower().replace(' ', '_')}", iconUnicode="\eb2a", color="black")  
                        st.metric(label=f"Sekolah {label}", value=f"{count}")

                # Tambahkan Jarak_Centroid sekolah
                for i in range(cluster_sekolah):
                    final_result_cleaned[f'Jarak_Centroid_{i}'] = final_data[f'Jarak_Centroid_{i}']

                # Tambahkan Centroid sekolah
                for i in range(cluster_sekolah):
                    centroid_col = f'Centroid_{i}'
                    if centroid_col in final_data.columns:
                        final_result_cleaned[centroid_col] = final_data[centroid_col]


                # Merge provinsi ke dalam tabel utama berdasarkan clustering
                final_result_cleaned = final_result_cleaned.merge(
                    province_clustered[['prop_sek', 'total_score', 'total_score_normalized', 'Label_Cluster']],
                    on='prop_sek',
                    how='left'
                ).rename(columns={'total_score': 'total_score_prov', 'total_score_normalized': 'total_score_normalized_prov', 'Label_Cluster': 'Label_Cluster_Prov'})
                
                if centroid_values is not None:
                     # Buat kolom centroid provinsi dan jaraknya di final_data
                    for i in range(cluster_provinsi):
                        final_result_cleaned[f'Centroid_Prov_{i}'] = centroid_values[i]
                        final_result_cleaned[f'Jarak_Centroid_Prov_{i}'] = np.abs(final_result_cleaned['total_score_normalized_prov'] - centroid_values[i])
                else:
                    for i in range(cluster_provinsi):
                        final_result_cleaned[f'Centroid_Prov_{i}'] = 0
                        final_result_cleaned[f'Jarak_Centroid_Prov_{i}'] = 0

                # Ambil semua kolom Centroid dan Jarak dari hasil clustering kota
                city_centroid_cols = [col for col in city_clustered.columns if col.startswith('Centroid_') or col.startswith('Jarak_Centroid_')]

                # Merge ke final_result_cleaned
                final_result_cleaned = final_result_cleaned.merge(
                    city_clustered[['prop_sek', 'kota_sek', 'total_score', 'total_score_normalized', 'Label_Cluster']],
                    on=['prop_sek', 'kota_sek'],
                    how='left'
                ).rename(columns={
                    'total_score': 'total_score_city',
                    'total_score_normalized': 'total_score_normalized_city',
                    'Label_Cluster': 'Label_Cluster_City'
                })

                # Sorting berdasarkan total_score_prov dan total_score_city
                final_result_cleaned = final_result_cleaned.sort_values(
                    by=['total_score_prov', 'total_score_city', 'skor_akhir'],
                    ascending=[False, False, False]
                )

                # 6. Tampilkan tabel dengan hasil yang sudah diurutkan
                if not final_result_cleaned.empty:
                    columns = [
                        ("prop_sek", "Provinsi"),
                        ("kota_sek", "Kota Sekolah"),
                        ("nama_sekolah", "Nama Sekolah"),
                        ("total_pendaftar", "Total Pendaftar"),
                        ("total_lulus", "Total Lulus Seleksi"),
                        ("total_regist", "Total Registrasi"),
                        ("total_batal", "Total Batal"),
                        ("bobot_waktu", "Skor Waktu Pendaftaran"),
                        ("skor_akhir", "Skor Akhir"),
                        ("skor_akhir_normalized", "Skor Normalisasi"),
                    ]
                    
                    # Dynamically add 'Jarak_Centroid_X' columns based on number of clusters
                    for i in range(cluster_sekolah):
                        columns.append((f'Jarak_Centroid_{i}', f'Jarak ke Centroid {i}'))

                    # Add "Cluster" column after the centroid columns
                    columns.append(("Cluster", "Cluster"))
                    column_names = [col[0] for col in columns]  # Ambil hanya nama kolomnya
                    render_table_with_pagination(final_result_cleaned, column_names, cluster_provinsi, cluster_kota, cluster_sekolah)

                else:
                    st.warning("Tidak ada data yang tersedia.")

if __name__ == '__main__':
    main()









    





















