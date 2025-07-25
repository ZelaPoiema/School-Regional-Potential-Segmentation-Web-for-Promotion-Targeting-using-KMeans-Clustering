import streamlit as st
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import altair as alt
import urllib.parse
import os
import datetime as dt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster  
from streamlit_extras.metric_cards import style_metric_cards  
import plotly.express as px
from function.nav import Nav
from function.home import add_logo
from function.dashboard_utlis import (
    get_cleaned_data_file,
    load_cleaned_data,
    count_registrants,
    count_lulus_seleksi,
    count_registered,
    count_batal,
    categorize_school,

)
st.set_page_config(
    page_title="PMB UKDW K-Means Clustering",
    layout="wide"
)
def main():
    # Cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        Nav("home")
        st.stop()
    Nav("home")
    pd.set_option('display.max_columns', None)
    

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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
    add_logo()
    # Pastikan file 'cleaned_data.xlsx' ada sebelum memuat data
    cleaned_df = load_cleaned_data()
    if cleaned_df.empty:
        st.error("Data tidak ditemukan. Pastikan file 'cleaned_data.xlsx' tersedia di folder 'uploaded_files'.")
        st.stop()
    filters = st.session_state.get("home", {})  # ambil filter khusus halaman 'home'
    provinsi_filter = filters.get("provinsi_filter", "Semua Provinsi")
    kabupaten_filter = filters.get("kabupaten_filter", [])
    fakultas_filter = filters.get("fakultas_filter", "Semua Fakultas")
    tahun_filter = filters.get("tahun_filter", list(cleaned_df['tahun'].unique()))


    # Info Tahun
    if len(tahun_filter) == len(cleaned_df['tahun'].unique()):
        tahun_message = f"Data Dashboard ini mencakup semua tahun: {cleaned_df['tahun'].min()} sampai {cleaned_df['tahun'].max()}"
    else:
        tahun_message = f"Data Dashboard ini mencakup tahun: {', '.join(map(str, sorted(tahun_filter)))}"

    st.info(tahun_message)

    # Build Query
    query_conditions = []

    if provinsi_filter != "Semua Provinsi":
        query_conditions.append(f"prop_sek == '{provinsi_filter}'")

    if kabupaten_filter:
        kabupaten_condition = " | ".join([f"kota_sek == '{kabupaten}'" for kabupaten in kabupaten_filter])
        query_conditions.append(f"({kabupaten_condition})")

    if fakultas_filter != "Semua Fakultas":
        prodi_in_fakultas = fakultas_reference.get(fakultas_filter, [])
        prodi_condition = " | ".join(
            [f"pilihan1 == '{prodi}'" for prodi in prodi_in_fakultas] +
            [f"pilihan2 == '{prodi}'" for prodi in prodi_in_fakultas]
        )
        query_conditions.append(f"({prodi_condition})")

    if tahun_filter:
        tahun_condition = " | ".join([f"tahun == {tahun}" for tahun in tahun_filter])
        query_conditions.append(f"({tahun_condition})")

    # Gabungkan query
    query_string = " and ".join(query_conditions)
    filtered_df = cleaned_df.query(query_string) if query_conditions else cleaned_df.copy()


    # Pastikan data tersedia
    if 'filtered_df' in locals() and not filtered_df.empty:
        # Column layout for metrics
        col1, col2, col3, col4 = st.columns(4, gap='small')
        def format_angka(angka):
            return "{:,.0f}".format(angka).replace(",", ".")
        with col1:
            registrants_count = count_registrants(filtered_df)
            st.metric(label="Pendaftar", value=format_angka(registrants_count))
        with col2:
            lulus_count = count_lulus_seleksi(filtered_df)
            st.metric(label="Lulus Seleksi", value=format_angka(lulus_count))
        with col3:
            tidak_lulus_count = count_registered(filtered_df)
            st.metric(label="Registrasi", value=format_angka(tidak_lulus_count))
        with col4:
            batal_count = count_batal(filtered_df)
            st.metric(label="Undur Diri", value=format_angka(batal_count))  # Tampilkan jumlah yang batal
        # Tambahkan gaya kartu metrik
        style_metric_cards(background_color="#FFFFFF", border_left_color="#686664", border_color="#000000", box_shadow="#F71938")
    else:
        st.warning("No data available. Please upload a CSV file in the 'Clustering' page.")
        
    
    col1, col2, col3 = st.columns([1, 1, 1], gap='small')
    # Plotly Styling Template
    PLOTLY_TEMPLATE = "plotly_white"
    with col1:
        # Gender comparison chart
        gender_counts = filtered_df['kelamin'].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]

        # Filter out the "Tidak Diketahui" value
        gender_counts = gender_counts[gender_counts['Gender'] != 'Tidak Diketahui']


        fig_gender = px.pie(
            gender_counts,
            names="Gender",
            values="Count",
            title="Perbandingan Gender Pendaftar",  # Judul grafik
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        # Update layout untuk memposisikan title di tengah dan memberi warna orange
        fig_gender.update_layout(
            height=300,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="Perbandingan Gender Pendaftar",  # Judul
                x=0.5,  # Posisi horizontal, 0.5 berarti di tengah
                xanchor="center",  # Titik acuan anchor di tengah
                yanchor="top",  # Titik acuan anchor di atas
                font=dict(
                    size=16,  # Ukuran font title
                    color="orange"  # Warna font title
                )
            ),
            showlegend=True,
            legend_title="Gender",
            template=PLOTLY_TEMPLATE
        )

        st.plotly_chart(fig_gender, use_container_width=True)
        
        
        # Top 10 Kabupaten Pendaftar
        # Aggregate by 'Kabupaten' and sort by the count of registrants
        top_kabupaten = filtered_df.groupby('kota_sek').size().reset_index(name='Count')
        top_kabupaten = top_kabupaten.sort_values(by='Count', ascending=False).head(10)

        # Plotly Bar Chart
        fig_kabupaten = px.bar(
            top_kabupaten,
            x="Count",  # Jumlah pendaftar
            y="kota_sek",  # Nama kabupaten
            orientation="h",  # Orientasi horizontal
            title="10 Besar Kabupaten Pendaftar",  # Judul grafik
            color_discrete_sequence=["orange"] * len(top_kabupaten)  # Warna batang grafik
        )

        # Update layout untuk gaya dan posisi elemen
        fig_kabupaten.update_layout(
            height=330,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="10 Besar Kabupaten Pendaftar",  # Judul grafik
                x=0.5,  # Posisi horizontal di tengah
                xanchor="center",  # Titik anchor di tengah
                yanchor="top",  # Titik anchor di atas
                font=dict(
                    size=16,  # Ukuran font judul
                    color="orange"  # Warna font judul
                )
            ),
            xaxis=dict(
                title="Jumlah Pendaftar",  # Judul sumbu X
                showgrid=True,
                gridcolor="#ececec"
            ),
            yaxis=dict(
                title="Kabupaten",  # Judul sumbu Y
                categoryorder="total ascending",  # Urutkan berdasarkan nilai X (Count)
                categoryarray=top_kabupaten['Count'],  # Gunakan data jumlah untuk pengurutan
                showgrid=False
            ),
            plot_bgcolor="rgba(0,0,0,0)",  # Latar belakang transparan
            paper_bgcolor="rgba(0,0,0,0)",  # Latar belakang kertas transparan
        )

        # Menambahkan angka statistik di ujung batang
        fig_kabupaten.update_traces(
            text=top_kabupaten['Count'],  # Menampilkan angka jumlah pendaftar
            textposition='outside',  # Menampilkan angka di luar batang
            texttemplate='%{text}',  # Format angka statistik
            textfont=dict(size=9)
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig_kabupaten, use_container_width=True)

    # Step 1: Extract Jenis Sekolah (e.g., SMA, MA, SMK) for Jenjang Pendidikan
    filtered_df['Jenis Sekolah'] = filtered_df['nama_sekolah'].str.extract(r'^(SMA|SMK|STM|PKBM)', expand=False)
    filtered_df['Jenis Sekolah'] = filtered_df['Jenis Sekolah'].fillna('Lainnya')

    # Step 2: Aggregate counts for each school type
    school_type_counts = filtered_df['Jenis Sekolah'].value_counts().reset_index()
    school_type_counts.columns = ['Jenis Sekolah', 'Count']
    with col2:
        # Plotly Donut Chart
        fig_jenjang = px.pie(
            school_type_counts,
            names="Jenis Sekolah",  # Kolom untuk kategori
            values="Count",       # Kolom untuk nilai
            title="Jenjang Pendidikan Pendaftar",  # Judul grafik
            hole=0.4,  # Menjadikan pie chart menjadi donat
            color_discrete_sequence=px.colors.qualitative.Set3  # Skema warna
        )

        # Update layout untuk memposisikan title di tengah dan memberi warna orange
        fig_jenjang.update_layout(
            height=300,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="Jenjang Pendidikan Pendaftar",  # Judul
                x=0.5,  # Posisi horizontal, 0.5 berarti di tengah
                xanchor="center",  # Anchor judul di tengah
                yanchor="top",  # Anchor judul di atas
                font=dict(
                    size=16,  # Ukuran font judul
                    color="orange"  # Warna font judul
                )
            ),
            showlegend=True,  # Menampilkan legenda
            legend_title="Jenis Sekolah",  # Judul legenda
            template="plotly_white"  # Template Plotly
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig_jenjang, use_container_width=True)

        # Mengelompokkan data berdasarkan nama_sekolah dan prop_sek lalu menghitung jumlah pendaftar
        grouped_schools = (
            filtered_df[filtered_df['nama_sekolah'] != 'UNKNOWN']  # Mengabaikan 'UNKNOWN' di nama_sekolah
            .groupby(['nama_sekolah'])
            .size()
            .reset_index(name="Count")  # Tambahkan kolom jumlah pendaftar
        )
        top_schools = grouped_schools.nlargest(10, "Count")

        # Membuat bar chart menggunakan Plotly
        fig_top_schools = px.bar(
            top_schools,
            x="Count",  # Jumlah pendaftar
            y="nama_sekolah",  # Nama sekolah
            orientation="h",  # Orientasi horizontal
            title="10 Besar Asal Sekolah Pendaftar ",  # Judul
            color_discrete_sequence=["orange"]  # Warna batang
        )

        # Update layout untuk styling
        fig_top_schools.update_layout(
            height=330,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="10 Besar Asal Sekolah Pendaftar",  # Judul grafik
                x=0.5,  # Posisikan di tengah
                xanchor="center",  # Anchor di tengah
                yanchor="top",  # Anchor di atas
                font=dict(
                    size=16,  # Ukuran font judul
                    color="orange"  # Warna font judul
                )
            ),
            xaxis=dict(
                title="Jumlah Pendaftar",  # Judul sumbu X
                showgrid=True,  # Tampilkan grid sumbu X
                gridcolor="#ececec"  # Warna grid
            ),
            yaxis=dict(
                title="Nama Sekolah",  # Judul sumbu Y
                categoryorder="total ascending",  # Urutkan berdasarkan jumlah
                showgrid=False  # Sembunyikan grid pada sumbu Y
            ),
            plot_bgcolor="rgba(0,0,0,0)",  # Latar belakang plot transparan
            paper_bgcolor="rgba(0,0,0,0)",  # Latar belakang kertas transparan
        )

        # Menambahkan angka statistik di ujung batang
        fig_top_schools.update_traces(
            text=top_schools['Count'],  # Menampilkan angka jumlah pendaftar
            textposition='outside',  # Menampilkan angka di luar batang
            texttemplate='%{text}',  # Format angka statistik
            textfont=dict(size=9)
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig_top_schools, use_container_width=True)
        

    # Apply the categorization to Sekolah column
    filtered_df['Status Pendidikan'] = filtered_df['nama_sekolah'].apply(categorize_school)

    with col3:
        status_pendidikan_data = filtered_df['Status Pendidikan'].value_counts().reset_index()
        status_pendidikan_data.columns = ['Category', 'Value']
        # Plotly Donut Chart
        fig_status = px.pie(
            status_pendidikan_data,
            names="Category",  # Kolom untuk kategori
            values="Value",    # Kolom untuk nilai
            title="Status Pendidikan Pendaftar",  # Judul grafik
            hole=0.4,  # Menjadikan pie chart menjadi donat
            color_discrete_sequence=px.colors.qualitative.Pastel  # Skema warna
        )

        # Update layout untuk memposisikan title di tengah dan memberi warna orange
        fig_status.update_layout(
            height=300,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="Status Pendidikan Pendaftar",  # Judul
                x=0.5,  # Posisi horizontal, 0.5 berarti di tengah
                xanchor="center",  # Anchor judul di tengah
                yanchor="top",  # Anchor judul di atas
                font=dict(
                    size=16,  # Ukuran font judul
                    color="orange"  # Warna font judul
                )
            ),
            showlegend=True,  # Menampilkan legenda
            legend_title="Kategori",  # Judul legenda
            template="plotly_white"  # Template Plotly
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig_status, use_container_width=True)

        # Menghitung jumlah pendaftar berdasarkan "Pilihan 1" dan "Pilihan 2"
        df_pivoted = pd.concat([
            filtered_df['pilihan1'].value_counts().rename_axis('Jurusan').reset_index(name='count').assign(Pilihan='Pilihan 1'),
            filtered_df['pilihan2'].value_counts().rename_axis('Jurusan').reset_index(name='count').assign(Pilihan='Pilihan 2')
        ])
        # Filter untuk menghilangkan jurusan "Tidak Memilih"
        df_pivoted = df_pivoted[df_pivoted['Jurusan'].str.lower() != 'tidak memilih']

        if fakultas_filter != "Semua Fakultas":
            df_pivoted = df_pivoted[df_pivoted['Jurusan'].isin(prodi_in_fakultas)]

        fig = px.bar(
            df_pivoted,
            x="count",
            y="Jurusan",
            color="Pilihan",
            barmode="stack",  # Ganti dari 'group' menjadi 'stack' agar batangnya bertumpuk
            orientation="h",
            title="Perbandingan Pemilihan Prodi Oleh Pendaftar",
            color_discrete_map={
                'Pilihan 1': 'steelblue',
                'Pilihan 2': '#B0C4DE'
            }
        )
        # Menyesuaikan layout grafik
        fig.update_layout(
            height=330,  # Tinggi grafik tetap
            autosize=True,  # Grafik otomatis menyesuaikan lebar
            margin=dict(l=10, r=10, t=40, b=10),  # Kurangi margin internal grafik
            title=dict(
                text="Perbandingan Pemilihan Prodi Oleh Pendaftar",
                x=0.5,
                xanchor="center",
                yanchor="top",
                font=dict(
                    size=16,
                    color="orange"
                )
            ),
            xaxis=dict(
                title="Jumlah Pendaftar",
                showgrid=True,
                gridcolor="#ececec"
            ),
            yaxis=dict(
                title="Jurusan",
                categoryorder="total ascending",  # Untuk memastikan urutan berdasarkan total pendaftar
                showgrid=False
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        # Menampilkan grafik di Streamlit
        st.plotly_chart(fig, use_container_width=True)
        


if __name__ == "__main__":
    main()
