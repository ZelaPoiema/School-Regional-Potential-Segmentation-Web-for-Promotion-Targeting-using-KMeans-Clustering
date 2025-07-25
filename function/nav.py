import pandas as pd
import os
import streamlit as st
import hashlib
from function.clustering_utils import (
    calculate_weighted_score,
    cluster_by_province,
    normalize_total_score_prov,
    hitung_jumlah_cluster_optimal_provinsi,
    cluster_program_study_by_province1,
    normalize_total_score_prov_prodi,
    hitung_jumlah_cluster_optimal_provinsi_prodi,
    process_filtered_data,
    get_df_hash,
)

from function.nav_utils import get_file_hash, load_cleaned_data, DATA_FILE

# Function to set filters based on page name
def set_filters(page_name):
    # Ensure session state is initialized for filters
    if page_name not in st.session_state:
        st.session_state[page_name] = {}
    filters = st.session_state[page_name]
    if os.path.exists(DATA_FILE):
        file_hash = get_file_hash(DATA_FILE)
        cleaned_df = load_cleaned_data(file_hash)  # ← gunakan hash sebagai cache key
    else:
        st.error("❌ File 'cleaned_data.xlsx' tidak ditemukan.")
        return

    if cleaned_df.empty:
        st.error("📂 Dataset kosong.")
        return

    if page_name == "home":
        # Home-specific filters: Provinsi, Kabupaten, Fakultas, Tahun
        filters['provinsi_filter'] = st.sidebar.selectbox(
            "Provinsi:",
            options=["Semua Provinsi"] + list(cleaned_df['prop_sek'].dropna().unique())
        )
        kabupaten_options = pd.Series(cleaned_df[cleaned_df['prop_sek'] == filters['provinsi_filter']]['kota_sek'].dropna())
        kabupaten_counts = kabupaten_options.value_counts()
        filters['kabupaten_filter'] = st.sidebar.multiselect(
            "Kabupaten:",
            options=sorted(kabupaten_options.unique()),
            default=kabupaten_counts.head(10).index.tolist()
        )
        # Fakultas mapping
        fakultas_mapping = {
            "Sistem Informasi": "Fakultas Teknologi Informasi",
            "Informatika": "Fakultas Teknologi Informasi",
            "Arsitektur": "Fakultas Arsitektur dan Desain",
            "Desain Produk": "Fakultas Arsitektur dan Desain",
            "Manajemen": "Fakultas Bisnis",
            "Akuntansi": "Fakultas Bisnis",
            "Biologi": "Fakultas Bioteknologi",
            "Pendidikan Dokter": "Fakultas Kedokteran",
            "Pendidikan Bahasa Inggris": "Fakultas Kependidikan dan Humaniora",
            "Studi Humanitas": "Fakultas Kependidikan dan Humaniora",
            "Filsafat Keilahian": "Fakultas Teologi",
        }
        # Mapping program studi ke fakultas
        fakultas_reference = {
            "Fakultas Teologi": ["Filsafat Keilahian"],
            "Fakultas Arsitektur dan Desain": ["Arsitektur", "Desain Produk"],
            "Fakultas Bioteknologi": ["Biologi"],
            "Fakultas Bisnis": ["Manajemen", "Akuntansi"],
            "Fakultas Teknologi Informasi": ["Informatika", "Sistem Informasi"],
            "Fakultas Kedokteran": ["Pendidikan Dokter"],
            "Fakultas Kependidikan dan Humaniora": ["Pendidikan Bahasa Inggris", "Studi Humanitas"],
        }
        # Mengubah nilai fakultas berdasarkan pemetaan
        fakultas_baru = fakultas_mapping.get(st.session_state.fakultas, st.session_state.fakultas)
        # Filter Fakultas berdasarkan role
        if st.session_state.role == "admisi":
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=["Semua Fakultas"] + list(fakultas_reference.keys())
            )
        elif st.session_state.role == "dekan":
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=[st.session_state.fakultas]
            )
         # Menggunakan fakultas_baru dalam selectbox
        elif st.session_state.role == "kaprodi": 
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=[fakultas_baru]
            )
        filters['tahun_filter'] = st.sidebar.multiselect(
            "Tahun:",
            options=cleaned_df['tahun'].unique(),
            default=cleaned_df['tahun'].unique()
        )
    elif page_name == "peta":
        # Fakultas mapping
        fakultas_mapping = {
            "Sistem Informasi": "Fakultas Teknologi Informasi",
            "Informatika": "Fakultas Teknologi Informasi",
            "Arsitektur": "Fakultas Arsitektur dan Desain",
            "Desain Produk": "Fakultas Arsitektur dan Desain",
            "Manajemen": "Fakultas Bisnis",
            "Akuntansi": "Fakultas Bisnis",
            "Biologi": "Fakultas Bioteknologi",
            "Pendidikan Dokter": "Fakultas Kedokteran",
            "Pendidikan Bahasa Inggris": "Fakultas Kependidikan dan Humaniora",
            "Studi Humanitas": "Fakultas Kependidikan dan Humaniora",
            "Filsafat Keilahian": "Fakultas Teologi",
        }
        # Mapping program studi ke fakultas
        fakultas_reference = {
            "Fakultas Teologi": ["Filsafat Keilahian"],
            "Fakultas Arsitektur dan Desain": ["Arsitektur", "Desain Produk"],
            "Fakultas Bioteknologi": ["Biologi"],
            "Fakultas Bisnis": ["Manajemen", "Akuntansi"],
            "Fakultas Teknologi Informasi": ["Informatika", "Sistem Informasi"],
            "Fakultas Kedokteran": ["Pendidikan Dokter"],
            "Fakultas Kependidikan dan Humaniora": ["Pendidikan Bahasa Inggris", "Studi Humanitas"],
        }
        # Mengubah nilai fakultas berdasarkan pemetaan
        fakultas_baru = fakultas_mapping.get(st.session_state.fakultas, st.session_state.fakultas)
        # Filter Fakultas berdasarkan role
        if st.session_state.role == "admisi":
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=["Semua Fakultas"] + list(fakultas_reference.keys())
            )
        elif st.session_state.role == "dekan":
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=[st.session_state.fakultas]
            )
         # Menggunakan fakultas_baru dalam selectbox
        elif st.session_state.role == "kaprodi": 
            filters['fakultas_filter'] = st.sidebar.selectbox(
                "Fakultas:",
                options=[fakultas_baru]
            )
        filters['tahun_filter'] = st.sidebar.multiselect(
            "Tahun:",
            options=cleaned_df['tahun'].unique(),
            default=cleaned_df['tahun'].unique()
        )
    elif page_name == "clustering":
        df_hash = get_df_hash(cleaned_df)
        # Hitung skor berbobot (juga sebaiknya dibuat cached, seperti calculate_weighted_score_cached())
        final, grouped_data_normalized = calculate_weighted_score(cleaned_df, df_hash)
        # Hitung hash dari final_data untuk cache cluster_by_province
        df_hash_prov = get_df_hash(final)

        # Cluster provinsi
        province_data = cluster_by_province(final, df_hash_prov)
        province_clustered = normalize_total_score_prov(province_data)
        # Rename kolom untuk konsistensi dengan parameter fungsi
        province_clustered = province_clustered.rename(columns={
            'total_score_normalized': 'total_score_normalized_prov'
        })
        # Merge hasil normalisasi ke final data
        final = final.merge(
            province_clustered[['prop_sek', 'total_score_normalized_prov']],
            on='prop_sek',
            how='left'
        )
        # Hitung jumlah cluster optimal untuk provinsi
        jumlah_cluster_optimal_prov = hitung_jumlah_cluster_optimal_provinsi(
            province_clustered,
            score_column='total_score_normalized_prov',
            n_cluster_options=[2, 3, 4]
        )
        if st.session_state.role == "admisi":
            valid_program_studi = pd.concat([cleaned_df['pilihan1'], cleaned_df['pilihan2']])
            valid_program_studi = valid_program_studi[valid_program_studi != 'Tidak Memilih'].unique()
            filters['program_studi_filter'] = st.sidebar.selectbox(
                "Pilih Program Studi",
                options=["Tidak Ada"] + sorted(valid_program_studi.tolist())
            )
        elif st.session_state['role'] == 'dekan':
            fakultas_user = st.session_state.get('fakultas', None)
            if fakultas_user and fakultas_user in fakultas_reference:
                valid_program_studi = fakultas_reference[fakultas_user]
                filters['program_studi_filter'] = st.sidebar.selectbox(
                    "Pilih Program Studi",
                    options=sorted(valid_program_studi)
                )
            else:
                valid_program_studi = pd.concat([cleaned_df['pilihan1'], cleaned_df['pilihan2']])
                valid_program_studi = valid_program_studi[valid_program_studi != 'Tidak Memilih'].unique()
                filters['program_studi_filter'] = st.sidebar.selectbox(
                    "Pilih Program Studi",
                    options=["Tidak Ada"] + sorted(valid_program_studi.tolist())
                )
        elif st.session_state['role'] == 'kaprodi':
            # Untuk role 'kaprodi', sesuaikan fakultas dengan prodi-nya
            fakultas_user = st.session_state.get('fakultas', None)
            filters['program_studi_filter'] = st.sidebar.selectbox(
                    "Pilih Program Studi",
                    options=fakultas_user
            )
        else:
            valid_program_studi = pd.concat([cleaned_df['pilihan1'], cleaned_df['pilihan2']])
            valid_program_studi = valid_program_studi[valid_program_studi != 'Tidak Memilih'].unique()
            filters['program_studi_filter'] = st.sidebar.selectbox(
                "Pilih Program Studi",
                options=["Tidak Ada"] + sorted(valid_program_studi.tolist())
            )
        # Clustering-specific filters: Provinsi, Kabupaten, Program Studi, Tahun, Cluster
        # Filter jumlah cluster per level
        filters['jumlah_cluster_provinsi'] = st.sidebar.selectbox(
            "Jumlah Cluster(K) Provinsi:",
            options=[2, 3, 4],
            index=0
        )
        if filters['program_studi_filter'] == "Tidak Ada":
            # Tidak memilih program studi, pakai hasil cluster provinsi biasa
            optimal_k = jumlah_cluster_optimal_prov['jumlah_cluster_optimal'].iloc[0]
            st.sidebar.markdown(
                f"<span style='color:blue'><b>K-Optimal Provinsi:</b> {optimal_k}</span>",
                unsafe_allow_html=True
            )
        else:
            # Proses clustering semua sekolah lebih dulu
            cluster_prov = filters['jumlah_cluster_provinsi']
            selected_prodi = filters['program_studi_filter']

            if selected_prodi != "Tidak Ada":
                filtered_df = cleaned_df[
                    (cleaned_df['pilihan1'] == selected_prodi) |
                    (cleaned_df['pilihan2'] == selected_prodi)
                ]
                filtered_df = filtered_df.copy()  # Tambahkan ini agar .loc/assignment aman
                filtered_df["program_studi"] = selected_prodi
            else:
                # Jika filter = "Tidak Ada", kita tetap harus buat kolom program_studi agar tidak error
                filtered_df = cleaned_df.copy()
                filtered_df["program_studi"] = filtered_df["pilihan1"]  # atau default value lain

            clustered_data, iteration_results_prodi = process_filtered_data(filtered_df, cluster_prov)
            clustered_data = clustered_data.drop_duplicates(subset=['nama_sekolah', 'kota_sek', 'prop_sek', 'program_studi'])
            provinsi_filter = filters['provinsi_filter']
            # 👇 Cek hanya jalankan clustering prodi-per-provinsi jika provinsi_filter = SEMUA atau Non-DIY&JATENG
            if provinsi_filter in ["SEMUA PROVINSI", "Non-DIY&JATENG"]:
                # Step 4: Proses clustering khusus program studi
                cluster_prodi = cluster_program_study_by_province1(clustered_data, selected_prodi)
                cluster_prodi_norm = normalize_total_score_prov_prodi(cluster_prodi)
                cluster_prodi_norm = cluster_prodi_norm.rename(columns={
                    'total_score_normalized': 'total_score_normalized_prov'
                })

                # Hitung jumlah cluster optimal untuk program studi per provinsi
                jumlah_cluster_optimal_prov_prodi = hitung_jumlah_cluster_optimal_provinsi_prodi(
                    cluster_prodi_norm,
                    score_column='total_score_normalized_prov',
                    n_cluster_options=[2, 3, 4]
                )

                optimal_k = jumlah_cluster_optimal_prov_prodi['jumlah_cluster_optimal'].iloc[0]
                st.sidebar.markdown(
                    f"<span style='color:green'><b>K-Optimal Provinsi (Prodi '{selected_prodi}'):</b> {optimal_k}</span>",
                    unsafe_allow_html=True
                )
            else:
                st.sidebar.markdown(
                    f"<span style='color:red'><b>K-Optimal Provinsi tidak dihitung karena filter provinsi spesifik.</b></span>",
                    unsafe_allow_html=True
                )
        filters['jumlah_cluster_kota'] = st.sidebar.selectbox(
            "Jumlah Cluster Kota:",
            options=[2, 3, 4],
            index=0
        )
        filters['jumlah_cluster_sekolah'] = st.sidebar.selectbox(
            "Jumlah Cluster Sekolah:",
            options=[2, 3, 4],
            index=0
        )
        
        filters['provinsi_filter'] = st.sidebar.selectbox(
            "Provinsi:",
            options=["SEMUA PROVINSI", "Non-DIY&JATENG"] + list(cleaned_df['prop_sek'].dropna().unique())
        )

        provinsi_filter = filters['provinsi_filter']

        if provinsi_filter == "Non-DIY&JATENG":
            kabupaten_options = (
                cleaned_df[~cleaned_df['prop_sek'].isin(["PROV. D.I. YOGYAKARTA", "PROV. JAWA TENGAH"])]
                ['kota_sek']
                .dropna()
                .drop_duplicates()
                .sort_values()
                .unique()
            )
        elif provinsi_filter == "SEMUA PROVINSI":
            kabupaten_options = (
                cleaned_df['kota_sek']
                .dropna()
                .drop_duplicates()
                .sort_values()
                .unique()
            )
        else:
            kabupaten_options = (
                cleaned_df[cleaned_df['prop_sek'] == provinsi_filter]['kota_sek']
                .dropna()
                .drop_duplicates()
                .sort_values()
                .unique()
            )

        filters['kabupaten_filter'] = st.sidebar.selectbox(
            "Kabupaten:",
            options=["SEMUA KABUPATEN"] + list(kabupaten_options)
        )

        filters['tahun_filter'] = st.sidebar.multiselect(
            "Pilih Data PMB Tahun:",
            options=cleaned_df['tahun'].unique(),
            default=cleaned_df['tahun'].unique()
        )
    if st.sidebar.button("⬅️ Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.fakultas = None
        st.switch_page("login.py")

def Nav(page_name):
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.sidebar.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; 
                        font-size: 16px; font-weight: bold; 
                        margin-bottom: 20px; color: #333;">
                👤 {st.session_state.role.upper()}
            </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.page_link('pages/home.py', label='Home', icon='🏠')
        
        if st.session_state.role == "admisi":
            st.sidebar.page_link('pages/user.py', label='User Setting', icon='⚙️')

        st.sidebar.page_link('pages/peta.py', label='Peta Pendaftar', icon='🌍') 
        st.sidebar.page_link('pages/clustering.py', label='Clustering', icon='💠')
        st.sidebar.page_link('pages/maps.py', label='Maps Clustering', icon='🌍')

        st.sidebar.markdown("<hr style='border: 1px solid #ccc; margin-top: 5px; margin-bottom: 35px;'>", unsafe_allow_html=True)
         # Hanya tampilkan filter jika bukan halaman user.py
        if page_name != "user":
            st.sidebar.header('Filter Data')
            set_filters(page_name)
            filters = st.session_state[page_name]
    else:
        st.sidebar.page_link("login.py", label="🔐 Login")




