import streamlit as st
import pandas as pd
def add_logo():
        st.markdown(
            """
            <style>
                [data-testid="stHeader"] {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #FFFFFF;
                    padding: 0;
                    margin: 0;
                    height: 60px;
                    position: relative;
                }
                .stButton button {
                    height: 38px;
                    margin-top: 50px;
                    width: 218px; /* Atur lebar tombol secara otomatis */
                    min-width: 218px; /* Tentukan lebar minimum tombol */
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

                /* Menimpa hanya padding atas dan bawah */
                .css-z5fcl4 {
                    padding-top: 0rem !important;  /* Padding atas */
                    padding-bottom: 0rem !important;  /* Padding bawah */
                    padding-left: 3rem !important;  /* Padding kiri */
                    padding-right: 3rem !important;  /* Padding kanan */
                }

                iframe[style] {
                    width: 1015px; /* Memastikan lebar tetap */
                    margin-top: 150px
                    height: 0px; /* Mengurangi tinggi iframe */
                    margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                    padding-bottom: 0 !important; /* Hilangkan padding bawah */
                }
                /* Mengubah tinggi iframe berdasarkan data-testid */
                [data-testid="stCustomComponentV1"] {
                    height: 235px !important;
                }

                [data-testid="stHeader"]::after {
                    content: "🏢 Dashboard PMB UKDW 📊";
                    font-size: 32px;
                    font-weight: bold;
                    color: orange;
                    position: absolute;
                    top: 50%;
                    left: 57%;
                    transform: translate(-50%, -50%);
                }
                [data-testid="stMainBlockContainer"] {
                    margin: 0px 20px 0 20px !important; /* Padding atas, kanan, bawah, kiri */
                    padding-top: 40px !important; /* Padding atas, kanan, bawah, kiri */
                    margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                    padding-bottom: 0 !important; /* Hilangkan padding bawah */
                    margin-top: 0
                }

                [data-testid="stHorizontalBlock"] {
                    margin-top: 0px !important; /* Kurangi jarak atas */
                    padding-top: 0px !important; /* Kurangi padding atas */
                    margin-bottom: 0px !important; /* Kurangi jarak bawah */
                    padding-bottom: 0px !important; /* Kurangi padding bawah */
                }

                [data-testid="stVerticalBlock"] {
                    margin-top: 0px !important; /* Kurangi jarak atas */
                    padding-top: 0px !important; /* Kurangi padding atas */
                    margin-bottom: 0px !important; /* Kurangi jarak bawah */
                    padding-bottom: 0px !important; /* Kurangi padding bawah */
                    height: 0px !important; /* Kurangi tinggi */
                }
                /* Sidebar logo */
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
                    background-repeat: no-repeat;
                    background-size: contain;
                    background-position: 50% 0%;
                    padding-top: 10px;
                    margin-top: 0; 
                }
                [data-testid="stSidebarNav"]::before {
                    margin-left: 20px;
                    margin-top: 20px;
                    font-size: 30px;
                    position: relative;
                    top: 100px;
                }
                
                /* Style untuk memperbaiki label metric card */
                [data-testid="metric-container"] {
                    margin: 0px;
                    padding: 0px;
                    font-size: 10px;  /* Sesuaikan ukuran teks */
                    height: 100px;  /* Sesuaikan tinggi card */
                    border: 1px solid #ccc;  /* Tambahkan border */
                    border-radius: 8px;  /* Tambahkan radius */
                }
                /* breakline for metric text         */
                [data-testid="stMetricLabel"] {
                    margin: 0px;
                    padding: 0px;
                    font-size: 20px; /* Sesuaikan ukuran nilai */
                    font-weight: bold; /* Buat teks nilai lebih tebal */
                }
                /* Nilai metric cards */
                [data-testid="stMetricValue"] {
                    margin: 0px;
                    padding: 0px;
                    margin-top: 0 !important;
                    margin-bottom: 0 !important;
                    font-size: 14px; /* Sesuaikan ukuran nilai */
                    font-weight: bold; /* Buat teks nilai lebih tebal */
                }
                div[data-testid="stMetric"], div[data-testid="metric-container"] {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    padding: 0px;
                    border-radius: 5px;
                    border-left: 0.5rem solid #686664 !important;
                    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
                    height: 80px;
                    display: flex;              /* Menggunakan flexbox */
                    flex-direction: column;     /* Atur elemen vertikal */
                    justify-content: center;    /* Vertikal: Posisikan elemen di tengah */
                    align-items: center;        /* Horizontal: Posisikan elemen di tengah */
                }

                .plot-container {
                    height: auto !important; /* Pastikan grafik tetap auto */
                    padding: 0 !important;   /* Hilangkan padding dalam container */
                    margin: 0 !important;    /* Hilangkan margin di sekitar grafik */
                    margin-top: 0 !important;
                    margin-bottom: 0 !important;
                }              
                .plot-container>div {
                    box-shadow: 0 0 2px #070505;
                    padding: 0px;
                    border-color: #000000;
                    margin-top: 0 !important;
                    margin-bottom: 0 !important;
                }
                [data-testid="stPlotlyChart"] {
                    box-shadow: none !important;
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                    margin-bottom: 0 !important;
                    padding-bottom: 0 !important;
                }  
                h3, h2, h1 {
                    margin: 0 !important; /* Hilangkan margin atas dan bawah */
                    margin-top: 0 !important;
                    padding-top: 0px !important;
                    padding-bottom: 5px !important; /* Hilangkan padding atas dan bawah */
                }
                .stElementContainer {
                    margin: 0 !important;
                    padding: 0 !important;
                    margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                    padding-bottom: 0 !important; /* Hilangkan padding bawah */
                    margin-top: 0
                    padding-top: 0
                }
                [data-testid="stAlert"], [data-testid="stAlertContainer"] {
                    height: 35px !important; /* Tinggi alert */
                    justify-content: center;  /* Posisikan konten secara horizontal di tengah */
                    align-items: center;      /* Posisikan konten secara vertikal di tengah */
                }

                [data-testid="stAlertContentInfo"] {
                    display: flex;            /* Flexbox untuk stAlertContentInfo */
                    justify-content: center;  /* Posisikan konten secara horizontal di tengah */
                    align-items: center;      /* Posisikan konten secara vertikal di tengah */
                }
                .st-emotion-cache-1mdzucs {
                    width: 951px;
                    height: 235px;
                    position: relative;
                    opacity: 0.33;
                    transition: opacity 1s ease-in 0.5s;
                }
                

            </style>
            """,
            unsafe_allow_html=True,
        )