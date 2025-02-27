import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

DATA_FILE = "pengeluaran_kas.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={"Kode": str})
    else:
        df = pd.DataFrame(columns=["Tanggal", "Kode", "Deskripsi", "Jumlah Barang", "Harga per Barang", "Total Harga"])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# Sidebar Navigation
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["Dashboard", "Input Data", "Data & Pencarian", "Kelola Data"])

# --- Dashboard ---
if menu == "Dashboard":
    st.title("📊 Dashboard Pengeluaran")
    if not df.empty:
        total_harga = df['Total Harga'].sum()
        avg_harga = df['Total Harga'].mean()
        count = len(df)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pengeluaran", f"Rp {total_harga:,}")
        col2.metric("Rata-rata Pengeluaran", f"Rp {avg_harga:.2f}")
        col3.metric("Jumlah Transaksi", count)
        
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], format="%d-%m-%Y", errors='coerce')
        df['Bulan'] = df['Tanggal'].dt.to_period('M').astype(str)
        monthly_summary = df.groupby('Bulan')['Total Harga'].sum()
        st.line_chart(monthly_summary)
    else:
        st.warning("Belum ada data untuk ditampilkan.")

# --- Input Data ---
elif menu == "Input Data":
    st.title("📝 Input Pengeluaran Baru")
    tanggal = st.date_input("Tanggal")
    kode = st.text_input("Kode (5 karakter, bisa angka atau huruf)", max_chars=5)
    deskripsi = st.text_area("Deskripsi")
    jumlah_barang = st.number_input("Jumlah Barang", min_value=1)
    harga_per_barang = st.number_input("Harga per Barang", min_value=0)
    total_harga = jumlah_barang * harga_per_barang

    if st.button("Simpan Data"):
        if len(kode) != 5:
            st.warning("Kode harus terdiri dari 5 karakter!")
        else:
            tanggal_str = tanggal.strftime("%d-%m-%Y")
            new_data = pd.DataFrame([[tanggal_str, kode.upper(), deskripsi, jumlah_barang, harga_per_barang, total_harga]], 
                                    columns=df.columns)
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success(f"Data tanggal {tanggal_str} berhasil disimpan!")

# --- Data & Pencarian ---
elif menu == "Data & Pencarian":
    st.title("🔍 Pencarian Data Pengeluaran")
    st.write("Kode yang tersedia:")
    st.markdown(", ".join(df["Kode"].unique().tolist()))
    
    kode_cari = st.selectbox("Pilih Kode (5 karakter) untuk Pencarian", df["Kode"].unique().tolist(), index=0 if not df.empty else None)
    
    if kode_cari:
        hasil = df[df["Kode"] == kode_cari]
        st.write("### Hasil Pencarian")
        st.dataframe(hasil, use_container_width=True)
    
    if st.button("Download CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Unduh CSV", data=csv, file_name="pengeluaran_kas.csv", mime='text/csv')

# --- Kelola Data (Edit & Hapus) ---
elif menu == "Kelola Data":
    st.title("✏️ Kelola Data")
    if not df.empty:
        st.write(df.style.set_properties(**{"background-color": "#f0f0f0", "border": "1px solid black"}))
        index = st.number_input("Masukkan Nomor Index untuk Edit/Hapus", min_value=0, max_value=len(df)-1, step=1)
        new_kode = st.text_input("Masukkan kode baru (5 karakter)", value=str(df.loc[index, "Kode"]).upper())
        if st.button("Edit Data"):
            if len(new_kode) != 5:
                st.warning("Kode harus terdiri dari 5 karakter!")
            else:
                df.loc[index, "Kode"] = new_kode
                save_data(df)
                st.success("Kode berhasil diperbarui!")
                st.rerun()
        
        if st.button("Hapus Data"):
            df = df.drop(index).reset_index(drop=True)
            save_data(df)
            st.success("Data berhasil dihapus")
            st.rerun()
    else:
        st.warning("Belum ada data untuk dikelola.")
