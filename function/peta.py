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
                height: 0px;
                position: relative;
            }
            span:empty {
                display: none !important;
            }
            /* Tombol "Hapus Semua Data" */
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
                padding-left: 0rem !important;  /* Padding kiri */
                padding-right: 0rem !important;  /* Padding kanan */
            }
            iframe[style] {
                width: 1015px; /* Memastikan lebar tetap */
                margin-top: 0px;
                height: 954px; /* Mengurangi tinggi iframe */
                margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                padding-bottom: 0 !important; /* Hilangkan padding bawah */
                padding-bottom: 0rem !important;  /* Padding bawah */
                padding-left: 0rem !important;  /* Padding kiri */
                padding-right: 0rem !important;  /* Padding kanan */
                display: block;
                border: none;
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
            div[data-testid="stVerticalBlock"] {
                margin-top: 0px !important; /* Kurangi jarak atas */
                padding-top: 0px !important; /* Kurangi padding atas */
                margin-bottom: 0px !important; /* Kurangi jarak bawah */
                padding-bottom: 0px !important; /* Kurangi padding bawah */
                height: auto !important;
            }
            [data-testid="stMainBlockContainer"] {
                margin: 0px 0px 0 0px !important; /* Padding atas, kanan, bawah, kiri */
                padding-top: 0px !important; /* Padding atas, kanan, bawah, kiri */
                margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                padding-bottom: 0 !important; /* Hilangkan padding bawah */
                margin-top: 0
                height: 954px !important;
            }
            [data-testid="stMain"] {
                margin: 0px 0px 0 0px !important; /* Padding atas, kanan, bawah, kiri */
                padding-top: 0px !important; /* Padding atas, kanan, bawah, kiri */
                margin-bottom: 0px !important; /* Hilangkan jarak bawah */
                padding-bottom: 0px !important; /* Hilangkan padding bawah */
                margin-top: 0px !important;
                height: 954px !important;
            }
            
            .st-emotion-cache-x39bl8 {
                width: 1117px;
                height: 954px; /* Mengurangi tinggi iframe */
                position: relative;
                opacity: 0.33;
                transition: opacity 1s ease-in 0.5s;
                padding-top: 0px !important; /* Padding atas, kanan, bawah, kiri */
                margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                padding-bottom: 0 !important; /* Hilangkan padding bawah */
                margin-top: 0 !important;
            }
            .st-emotion-cache-30qwot {
                width: 1111px;
                height: 0px; 
                position: relative;
                display: flex;
                flex: 1 1 0%;
                flex-direction: column;
                gap: 0rem;
            }
            @media (min-width: calc(736px + 8rem)) {
                .st-emotion-cache-t1wise {
                    padding-left: 0rem;
                    padding-right: 0rem;
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                }
            }
            div[data-testid="stVerticalBlock"] {
                margin-top: 0px !important; /* Kurangi jarak atas */
                padding-top: 0px !important; /* Kurangi padding atas */
                margin-bottom: 0px !important; /* Kurangi jarak bawah */
                padding-bottom: 0px !important; /* Kurangi padding bawah */
                height: 954px !important; /* Kurangi tinggi */
                gap: 0rem !important; /* Kurangi jarak antar elemen */
            }
            .stElementContainer {
                margin: 0 !important;
                padding: 0 !important;
                margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                padding-bottom: 0 !important; /* Hilangkan padding bawah */
                margin-top: 0
                padding-top: 0
            }
            /* Mengubah tinggi iframe berdasarkan data-testid */
            [data-testid="stCustomComponentV1"] {
                height: 954px !important;
                margin-bottom: 0 !important; /* Hilangkan jarak bawah */
                padding-bottom: 0 !important; /* Hilangkan padding bawah */
            }
            .st-emotion-cache-1v271fe {
                width: 1111px;
                height: 954px; /* Mengurangi tinggi iframe */
                position: relative;
                opacity: 0.33;
                transition: opacity 1s ease-in 0.5s;
            }
            .st-emotion-cache-auhqks {
                width: 1117px;
                height: 954px;
                position: relative;
                display: flex;
                flex: 1 1 0%;
                flex-direction: column;
                gap: 0rem; 
            }
            body, html, #root, .block-container, .main {
                height: 954px !important;
                overflow: hidden !important;
            }


            </style>
        """,
        unsafe_allow_html=True,
        )
