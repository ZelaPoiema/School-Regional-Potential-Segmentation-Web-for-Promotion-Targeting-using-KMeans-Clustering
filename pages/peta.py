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
from sklearn.cluster import DBSCAN
from function.peta import add_logo
from function.dashboard_utlis import (
    load_cleaned_data,
)
st.set_page_config(
    page_title="🌍 Peta Persebaran Pendaftar",
    layout="wide"
) 
def main():
    # Cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        Nav("peta")
        st.stop()
    Nav("peta")
    pd.set_option('display.max_columns', None)
    

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    add_logo()
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
    # Pastikan file 'cleaned_data.xlsx' ada sebelum memuat data
    cleaned_df = load_cleaned_data()
    if cleaned_df.empty:
        st.error("Data tidak ditemukan. Pastikan file 'cleaned_data.xlsx' tersedia di folder 'uploaded_files'.")
        st.stop()
    filters = st.session_state.get("home", {})  # ambil filter khusus halaman 'home'
    fakultas_filter = filters.get("fakultas_filter", "Semua Fakultas")
    tahun_filter = filters.get("tahun_filter", list(cleaned_df['tahun'].unique()))

    # Build Query
    query_conditions = []

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

    # Filter data dengan koordinat yang valid
    filtered_df['latitude'] = pd.to_numeric(filtered_df['latitude'], errors='coerce')
    filtered_df['longitude'] = pd.to_numeric(filtered_df['longitude'], errors='coerce')
    valid_data = filtered_df.dropna(subset=['latitude', 'longitude'])
    valid_data = valid_data[(valid_data['latitude'] >= -90) & (valid_data['latitude'] <= 90)]
    valid_data = valid_data[(valid_data['longitude'] >= -180) & (valid_data['longitude'] <= 180)]

    # Hitung jumlah pendaftar dan koordinat rata-rata per provinsi
    provinsi_group = valid_data.groupby('prop_sek').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'no_daftar': 'count'  # jumlah pendaftar
    }).reset_index()

    # Buat peta
    m = folium.Map(location=[-2.5, 118], zoom_start=5)
    # Tambahkan marker untuk setiap provinsi
    for _, row in provinsi_group.iterrows():
        jumlah = row['no_daftar']
        lat = row['latitude']
        lon = row['longitude']
        # Ukuran bubble disesuaikan dengan jumlah pendaftar
        if jumlah >= 1000:
            radius = 50
        elif jumlah >= 100:
            radius = 30
        elif jumlah >= 50:
            radius = 20
        else:
            radius = 10
        # Bubble berwarna biru
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=f"""
                <b>Provinsi:</b> {row['prop_sek']}<br>
                <b>Jumlah Pendaftar:</b> {jumlah}
            """,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.8
        ).add_to(m)
        # Tampilkan jumlah di atas bubble (tengah)
        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(
                html=f"""
                    <div style="font-size: 12px; font-weight: bold; color: white; text-align: center;">
                        {jumlah}
                    </div>
                """
            )
        ).add_to(m)
    # Tampilkan di Streamlit
    st_folium(m, use_container_width=True, height=1000)


if __name__ == '__main__':
    main()