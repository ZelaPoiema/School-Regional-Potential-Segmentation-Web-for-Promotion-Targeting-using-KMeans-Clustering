import streamlit as st
import pandas as pd
import time
from streamlit_extras.switch_page_button import switch_page
def main():
    st.set_page_config(page_title="Login", page_icon="🏫", layout="centered")

    st.markdown("""
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
        .stApp, body {    
            background-color: #F0FFFF;
        }

        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }

        .login-box {
            background-color: #f9f9f9;
            padding: 40px 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }

        .login-title {
            font-size: 24px;
            margin-bottom: 30px;
            color: #333333;
            font-weight: bold;
        }

        .login-icon {
            font-size: 40px;
            color: #333333;
        }

        /* Custom styling untuk tombol submit dengan warna hijau */
        .stButton > button {
            width: 100%;
            padding: 12px;
            font-weight: bold;
            font-size: 16px;
            background-color: #28a745; /* Warna hijau */
            color: white;
            border: none;
            border-radius: 6px;
            margin-top: 20px;
            cursor: pointer;
            transition: background-color 0.3s ease; /* Efek transisi */
        }

        .stButton > button:hover {
            background-color: #218838; /* Hijau lebih gelap saat hover */
        }

        .stButton > button:active {
            background-color: #1e7e34; /* Hijau lebih gelap saat ditekan */
        }

        .stButton > button:focus {
            outline: none; /* Menghilangkan outline saat fokus */
        }

        </style>
    """, unsafe_allow_html=True)

    # Tambahkan judul "Login" rata tengah
    st.markdown("""<h2 style="text-align:center; margin-bottom:20px;">Login</h2>""", unsafe_allow_html=True)

    # Username Input
    st.markdown('<div style="text-align:left; font-weight:bold; margin-top:10px;">👤 Username:</div>', unsafe_allow_html=True)
    username = st.text_input("", placeholder="Ketikkan username anda", label_visibility="collapsed")

    # Password Input
    st.markdown('<div style="text-align:left; font-weight:bold; margin-top:10px;">🔑 Password:</div>', unsafe_allow_html=True)
    password = st.text_input("", type="password", placeholder="Ketikkan password anda", label_visibility="collapsed")

    # Tombol Login
    login_button = st.button("LOGIN")

    if login_button:
        try:
            df_user = pd.read_excel("data_user.xlsx", sheet_name="users")
        except Exception as e:
            st.error(f"Gagal membaca file Excel: {e}")
            return

        user = df_user[df_user["username"] == username]

        if not user.empty and user.iloc[0]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user.iloc[0]["role"]
            st.session_state["fakultas"] = user.iloc[0].get("fakultas", None)
            st.success("Login berhasil! Mengarahkan ke dashboard...")
            time.sleep(3)
            switch_page("home")  # Tanpa ".py", cukup nama halaman
        else:
            st.error("❌ Username atau password salah.")

if __name__ == "__main__":
    main()
