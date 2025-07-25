import os
import pandas as pd
import hashlib
import streamlit as st

DATA_FILE = 'uploaded_files/cleaned_data.xlsx'

def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

@st.cache_data
def load_cleaned_data(file_hash):
    """Membaca file Excel dengan cache tergantung isi file."""
    return pd.read_excel(DATA_FILE, engine="openpyxl")

