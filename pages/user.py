from function.nav import Nav  
import streamlit as st
import pandas as pd
import time


st.set_page_config(page_title="User Setting", layout="wide")

# Load Data from Excel file
def load_data():
    try:
        return pd.read_excel("data_user.xlsx", sheet_name="users")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return pd.DataFrame()

# Save Data to Excel file
def save_data(df):
    try:
        df.to_excel("data_user.xlsx", sheet_name="users", index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# Function to delete a user
def delete_user(df, index):
    # Drop the row from DataFrame
    df = df.drop(index).reset_index(drop=True)
    # Save the updated DataFrame to Excel
    save_data(df)
    return df

# Main function for the app
def main():
    # Cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu.")
        Nav("user")
        st.stop()
    Nav("user")
    if st.sidebar.button("⬅️ Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.fakultas = None
        st.switch_page("login.py")
    st.title("👥 Manajemen Akun User")

    df = load_data()

    # Tombol Tambah User
    if st.button("➕ Buat Akun User"):
        st.session_state.show_form = True
        st.rerun()

    if "show_form" in st.session_state and st.session_state.show_form:
        st.markdown("### 📋 Form Akun User Baru")

        # Input fields untuk username, password, role, dan fakultas
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
        with col2:
            role = st.selectbox("Role", ["admisi", "dekan", "kaprodi"])

            # Menentukan pilihan fakultas berdasarkan role
            if role == "admisi":
                fakultas = st.selectbox(
                    "Fakultas/Prodi", ["Semua Fakultas"]
                )
            elif role == "dekan":
                fakultas = st.selectbox(
                    "Fakultas/Prodi",
                    [
                        "Fakultas Teknologi Informasi",
                        "Fakultas Arsitektur dan Desain",
                        "Fakultas Bisnis",
                        "Fakultas Kedokteran",
                        "Fakultas Bioteknologi",
                        "Fakultas Kependidikan dan Humaniora",
                        "Fakultas Teologi",
                    ]
                )
            elif role == "kaprodi":
                fakultas = st.selectbox(
                    "Prodi",
                    [
                        "Filsafat Keilahian",
                        "Arsitektur",
                        "Desain Produk",
                        "Biologi",
                        "Manajemen",
                        "Akuntansi",
                        "Informatika",
                        "Sistem Informasi",
                        "Pendidikan Dokter",
                        "Pendidikan Bahasa Inggris",
                        "Studi Humanitas",
                    ]
                )

        # Tombol Simpan
        if st.button("Simpan"):
            # Menyimpan data yang diisi ke dalam DataFrame dan file Excel
            new_data = {
                "username": username,
                "password": password,
                "role": role,
                "fakultas": fakultas,
                "timestamp": pd.Timestamp.now()  # Menambahkan timestamp
            }
            # Gabungkan data baru dengan DataFrame yang sudah ada dan urutkan berdasarkan timestamp
            df = pd.concat([pd.DataFrame([new_data]), df], ignore_index=True)
            df = df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)  # Urutkan berdasarkan timestamp
            save_data(df)
            st.success("✅ Akun berhasil ditambahkan.")
            time.sleep(3)  # Tunggu 3 detik agar user sempat lihat pesan
            del st.session_state.show_form
            st.rerun()




    # Tampilkan Tabel User
    if not df.empty:
        st.markdown("### 📄 Daftar Akun User")
        # Menampilkan Judul Kolom
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
        col1.write("**Username**")
        col2.write("**Password**")
        col3.write("**Role**")
        col4.write("**Fakultas**")
        col5.write("**Edit**")
        col6.write("**Delete**")
        for i, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
            col1.write(row["username"])
            col2.write("●●●●●●")  # sembunyikan password
            col3.write(row["role"])
            col4.write(row.get("fakultas"))

            # Tombol Edit
            if col5.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.session_state.show_edit_form = True
                st.rerun()

            # Tombol Delete
            if col6.button("🗑️", key=f"delete_{i}"):
                df = delete_user(df, i)  # Panggil fungsi untuk menghapus data
                st.success("✅ Akun berhasil dihapus.")
                time.sleep(3) 
                st.rerun()

         # Form Edit User
        if "show_edit_form" in st.session_state and st.session_state.show_edit_form:
            edit_index = st.session_state.edit_index
            edit_row = df.iloc[edit_index]
            st.markdown("### ✏️ Edit Akun")
            # Input fields untuk edit username, password, role, dan fakultas
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username", edit_row["username"])
                new_password = st.text_input("Password", edit_row["password"])
            with col2:
                new_role = st.selectbox("Role", ["admisi", "dekan", "kaprodi"], index=["admisi", "dekan", "kaprodi"].index(edit_row["role"]))

                # Menentukan pilihan fakultas berdasarkan role
                if new_role == "admisi":
                    new_fakultas = st.selectbox("Fakultas/Prodi", ["Semua Fakultas"])
                elif new_role == "dekan":
                    new_fakultas = st.selectbox(
                        "Fakultas",
                        [
                            "Fakultas Teknologi Informasi",
                            "Fakultas Arsitektur dan Desain",
                            "Fakultas Bisnis",
                            "Fakultas Kedokteran",
                            "Fakultas Bioteknologi",
                            "Fakultas Kependidikan dan Humaniora",
                            "Fakultas Teologi",
                        ]
                    )
                elif new_role == "kaprodi":
                    new_fakultas = st.selectbox(
                        "Prodi",
                        [
                            "Filsafat Keilahian",
                            "Arsitektur",
                            "Desain Produk",
                            "Biologi",
                            "Manajemen",
                            "Akuntansi",
                            "Informatika",
                            "Sistem Informasi",
                            "Pendidikan Dokter",
                            "Pendidikan Bahasa Inggris",
                            "Studi Humanitas",
                        ]
                    )

            # Tombol Update
            if st.button("Update"):
                # Update data pada df
                df.at[edit_index, "username"] = new_username
                df.at[edit_index, "password"] = new_password
                df.at[edit_index, "role"] = new_role
                df.at[edit_index, "fakultas"] = new_fakultas

                # Simpan perubahan ke Excel
                save_data(df)

                # Tampilkan pesan sukses
                st.success("✅ Data berhasil diperbarui.")
                time.sleep(3)  # Tunggu 3 detik agar user sempat lihat pesan
                del st.session_state.show_edit_form
                st.rerun()


    else:
        st.info("Belum ada akun user.")

if __name__ == "__main__":
    main()
