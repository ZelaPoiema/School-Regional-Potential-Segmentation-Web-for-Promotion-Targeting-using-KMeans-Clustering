import streamlit as st
import pandas as pd



def add_logo():
    st.markdown( 
        """
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=things_to_do" />
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=search" />
        <h1 style='text-align: center; color: orange;'>K-Means Clustering</h1>
        <style>
            .material-symbols-outlined {
                font-variation-settings:
                'FILL' 0,
                'wght' 400,
                'GRAD' 0,
                'opsz' 24;
                vertical-align: middle;
                margin-right: 8px; /* Memberi jarak antara ikon dan teks input */
            }
            [data-testid="stSidebar"]::before {
                content: "";
                display: block;
                background-image: url(https://sikerma.ukdw.ac.id/assets/images/logo-ukdw-2.png);
                background-repeat: no-repeat;
                background-position: top center;
                background-size: contain;
                height: 80px; /* Tinggi logo */
                margin-top: 10px; /* Jarak sebelum logo */
            }
            [data-testid="stSidebarNav"] {
                background-image: url(https://raw.githubusercontent.com/christianheins/wggesucht/main/images/4.jpg);
                background-repeat: no-repeat;
                background-size: contain;
                background-position: 50% 0%;
                padding-top: 10px;
            }
            div[data-testid="stVerticalBlock"] {
                min-width: 80px !important; /* Sesuaikan sesuai kebutuhan */
                margin-bottom: 0px;
            }
            [data-testid="stSidebarNav"]::before {
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }

            /* Gaya untuk tombol download */
            .stDownloadButton > button {
                height: 38px; /* Sesuaikan tinggi tombol */
                margin-top: 0;
                width: auto; /* Atur lebar tombol secara otomatis */
                min-width: 160px; /* Tentukan lebar minimum tombol */
                margin-right: 0px;  /* Memberikan sedikit jarak antara tombol */
                vertical-align: middle;
                background-color: #4CAF50; /* Warna latar belakang tombol */
                color: white; /* Warna teks tombol */
                font-weight: bold; /* Tebalkan teks tombol */
                border-radius: 5px; /* Sudut tombol yang membulat */
                border: none; /* Menghapus border default */
                cursor: pointer; /* Menambahkan kursor pointer */
                padding: 0 15px; /* Padding horizontal agar tombol tidak terlalu sempit */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Menambahkan bayangan lembut */
                transition: background-color 0.3s, transform 0.3s; /* Transisi untuk hover */
            }

            .stDownloadButton > button:hover {
                background-color: #45a049; /* Warna latar belakang saat hover */
                transform: translateY(-2px); /* Efek angkat tombol saat hover */
            }

            .stDownloadButton > button:active {
                transform: translateY(1px); /* Efek saat tombol ditekan */
            }

            /* Menyusun input teks dengan ikon */
            .stTextInput > div { 
                padding: 0; 
                margin: 0; 
                position: relative; /* Agar ikon bisa diposisikan di dalam input */
            }

            .stTextInput input {
                height: 38px; /* Sesuaikan tinggi input */
                margin-top: 0;
                margin-bottom: 0;
                vertical-align: middle;
                padding-left: 30px; /* Memberi ruang untuk ikon di kiri */
                width: 500px;
            }

            /* Menambahkan ikon pencarian */
            .stTextInput input::before {
                content: "\e8b6"; /* Unicode untuk ikon pencarian dari FontAwesome */
                font-family: 'Font Awesome 5 Free'; /* Menggunakan font FontAwesome */
                font-weight: 900; /* Mengatur ketebalan font */
                position: absolute;
                left: 10px; /* Posisi ikon di kiri input */
                top: 50%; /* Menempatkan ikon di tengah vertikal */
                transform: translateY(-50%); /* Menyelaraskan ikon vertikal */
                color: #555; /* Warna ikon */
            }
            /* Tombol "Hapus Semua Data" */
            .stButton button {
                height: 38px;
                width: auto; /* Atur lebar tombol secara otomatis */
                min-width: 180px; /* Tentukan lebar minimum tombol */
                background-color: #FF4F4F; /* Warna latar belakang merah */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                cursor: pointer;
            }

            .stButton button:hover {
                background-color: #FF1A1A; /* Warna latar belakang saat hover */
            }

            div[data-testid="stSelectbox"] {
                width: 100% !important;  /* Pastikan selectbox mengikuti lebar container */
                min-width: 150px !important;  /* Mencegah terlalu kecil */
                max-width: 300px !important;  /* Batasi lebar maksimal */
            }

            .stSelectbox.custom-select > div {
                margin-right: 0px !important;  /* Hapus margin kanan */
                width: 100% !important;  /* Pastikan selectbox menyesuaikan lebar */
                min-width: 150px !important;  /* Tetapkan lebar minimum */
            }

            .stSelectbox.custom-select div[data-baseweb="select"] {
                margin-right: 0px !important;  /* Hapus margin kanan */
                width: 100% !important;
                min-width: 150px !important;
            }

            /* Menambahkan pengaturan kolom */
            .stColumn {
                display: flex;
                align-items: center;  /* Menyelaraskan kolom secara vertikal */
            }
            
            .stMetric {
                width: 170px; /* Atur lebar metric card */
                padding: 5px; /* Perkecil padding */
            }
            .st-emotion-cache-4itxuk {
                width: 100px;
                position: relative;
                opacity: 0.33;
                transition: opacity 1s ease-in 0.5s;
            }
            .st-emotion-cache-13sqq4h {
                width: 100px;
                position: relative;
                display: flex;
                flex: 1 1 0%;
                flex-direction: column;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


