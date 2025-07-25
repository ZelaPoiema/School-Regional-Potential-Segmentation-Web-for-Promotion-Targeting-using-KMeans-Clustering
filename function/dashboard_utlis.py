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

# Inisialisasi folder tempat file Excel disimpan
UPLOAD_FOLDER = 'uploaded_files'

# Fungsi untuk mendapatkan file cleaned_data.xlsx
def get_cleaned_data_file(folder_path, file_name='cleaned_data.xlsx'):
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        return file_path
    return None

# Fungsi untuk memuat data dari file Excel
def load_cleaned_data():
    file_path = get_cleaned_data_file(UPLOAD_FOLDER)
    if file_path:
        try:
            # Membaca file Excel
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            st.error(f"Error membaca file Excel: {e}")
            return pd.DataFrame()
        return df
    else:
        st.warning(f"File 'cleaned_data.xlsx' tidak ditemukan di folder '{UPLOAD_FOLDER}'.")
        return pd.DataFrame()
 # Modified functions to ensure they return a scalar value
def count_registrants(cleaned_data):
    # Drop duplicate 'no_daftar' entries
    unique_registrants = cleaned_data.drop_duplicates(subset='no_daftar')
    # Count the total number of unique registrants
    return unique_registrants.shape[0]
def count_lulus_seleksi(df):
    return df[~df['terima'].isna() & (df['terima'] != 'Tidak Lolos')].shape[0]
def count_registered(data, column_name='nim'):
    # Filter data untuk hanya yang memiliki NIM (bukan "Tidak Registrasi")
    registered = data[data[column_name] != 'Tidak Registrasi']
    # Hitung jumlah data yang sesuai
    return registered.shape[0]
def count_batal(cleaned_data):
    return cleaned_data['batal'].sum()

# Create new column for Status Pendidikan based on Sekolah    
def categorize_school(school_name):
        # Ensure the school name is a string and handle potential NaN (float) values
    if isinstance(school_name, str):
        school_name = school_name.upper()  # Normalisasi ke huruf besar untuk konsistensi
    else:
        school_name = ""  # or return a default value like "Unknown" or "Lainnya"
    # Kategori Negeri
    if any(keyword in school_name for keyword in ["SMA N", "SMK N", "SMAN", "SMKN", "SEKOLAH MENENGAH KEJURUAN N"]):
        return "Negeri"
    # Kategori Swasta
    elif any(keyword in school_name for keyword in ["SMA S", "SMK S", "SMA", "SMK", "SMAS", "SMKS"]):
        return "Swasta"
    else:
        return "Lainnya"  # Untuk nama sekolah yang tidak masuk kategori
def navigate_to_dashboard():
    # Check if user is logged in
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        # Logic to display dashboard content
        st.title("Dashboard")
        st.write("Welcome to the Dashboard!")

    else:
        st.write("Please login first to access the dashboard.")

