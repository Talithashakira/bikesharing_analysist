import os
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

# Load dataset
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(BASE_DIR, "main_data.csv")   
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    df["month"] = df["dteday"].dt.month
    df["year"] = df["dteday"].dt.year
    return df

# Fungsi untuk agregasi data bulanan
def create_monthly_users_df(df):
    monthly_users_df = df.groupby(["year", "month"]).agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_users_df["month_name"] = monthly_users_df["month"].apply(lambda x: month_names[x-1])
    
    return monthly_users_df

# Fungsi untuk agregasi data harian
def create_daily_users_df(df, start_date, end_date):
    daily_users_df = df[(df["dteday"] >= start_date) & (df["dteday"] <= end_date)].groupby("dteday").agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    return daily_users_df

# Load data
df = load_data()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, "e-bikes.jpeg")

# Sidebar Navigation
with st.sidebar:
    st.image(image_path, use_container_width=True)
    page = option_menu(
    "Pilih Halaman", ["Introduction", "Dashboard"],
    icons=["info-circle", "bar-chart"],
    menu_icon="",
    default_index=0,
    styles={
        "container": {"padding": "5!important", "background-color": "#161616"},
        "icon": {"color": "white", "font-size": "20px"},
        "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "color": "white"},
        "nav-link-selected": {"background-color": "#8c1af5", "font-weight": "bold", "color": "white"},
    }
)

# Dashboard Page
if page == "Dashboard":
    # Judul Utama Dashboard
    st.title(":rocket: Capital Bikeshare: Bike-Sharing Dashboard")
    st.markdown("---")
    
    st.header(":bar_chart: Monthly Count of Bikeshare Rides")
    selected_year = st.selectbox("Pilih Tahun:", options=[2011, 2012])
    
    monthly_users_df = create_monthly_users_df(df)
    filtered_df = monthly_users_df[monthly_users_df["year"] == selected_year]
    
    if not filtered_df.empty:
        fig = px.line(filtered_df, x="month_name", y=["casual", "registered"], markers=True,
                      title=f"Monthly Count of Bikeshare Rides ({selected_year})",
                      labels={"month_name": "Bulan", "value": "Total Rides", "variable": "User Type"},
                      color_discrete_map={"casual": "#8c1af5", "registered": "#ea33f7"},
                      line_shape="linear")
        
        fig.for_each_trace(lambda t: t.update(name="Casual Riders") if t.name == "casual" else t.update(name="Registered Riders"))
        fig.update_xaxes(tickangle=-45, tickmode="array", tickvals=filtered_df["month_name"])
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='DarkSlateGrey')))

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data untuk tahun yang dipilih.")

    time_period_labels = {1: "Morning", 2: "Afternoon", 3: "Evening", 4: "Night"}
    df["time_period"] = df["time_period"].map(time_period_labels)
    
    st.header(":bar_chart: Bikeshare Users by Time of the Day")
    selected_date = st.date_input("Pilih Tanggal:", df["dteday"].min())
    selected_date = pd.to_datetime(selected_date)
    filtered_df = df[df["dteday"].dt.date == selected_date.date()]
    
    time_period_df = filtered_df.groupby("time_period").agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()

    if not time_period_df.empty:
        fig = px.bar(time_period_df, x="time_period", y=["casual", "registered"],
                     title=f"Users Count by Time of the Day ({selected_date.date()})",
                     labels={"time_period": "Waktu dalam Sehari", "value": "Total Rides", "variable": "User Type"},
                     barmode="group",
                     color_discrete_map={"casual": "#8c1af5", "registered": "#ea33f7"},
                     category_orders={"time_period": ["Morning", "Afternoon", "Evening", "Night"]})
        
        fig.for_each_trace(lambda t: t.update(name="Casual Riders") if t.name == "casual" else t.update(name="Registered Riders"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data untuk tanggal yang dipilih.")

    # ✅ Tambahan: Grafik Bikeshare User by Day (Line Chart) dengan Rentang Tanggal Maksimal 14 Hari
    st.header(":bar_chart: Daily Count of Bikeshare Rides")
    st.write("Pilih rentang tanggal (maksimal 14 hari) untuk melihat jumlah pengguna harian:")

    # Filter rentang tanggal
    min_date = df["dteday"].min().date()
    max_date = df["dteday"].max().date()
    date_range = st.date_input("Pilih Rentang Tanggal:", [min_date, min_date + pd.Timedelta(days=13)])

    # Pastikan user memilih 2 tanggal
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        date_diff = (end_date - start_date).days
        
        # Validasi jika rentang tanggal lebih dari 14 hari
        if date_diff > 13:
            st.warning("⚠️ Rentang tanggal tidak boleh lebih dari 14 hari. Silakan pilih ulang.")
        else:
            daily_df = create_daily_users_df(df, start_date, end_date)

            if not daily_df.empty:
                fig = px.line(daily_df, x="dteday", y=["casual", "registered"], markers=True,
                              title=f"Daily Count of Bikeshare Rides ({start_date.date()} sampai {end_date.date()})",
                              labels={"dteday": "Tanggal", "value": "Total Rides", "variable": "User Type"},
                              color_discrete_map={"casual": "#8c1af5", "registered": "#ea33f7"},
                              line_shape="linear")
                
                fig.for_each_trace(lambda t: t.update(name="Casual Riders") if t.name == "casual" else t.update(name="Registered Riders"))
                fig.update_traces(marker=dict(size=6, line=dict(width=2)))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk rentang tanggal yang dipilih.")
    else:
        st.info("Silakan pilih rentang tanggal terlebih dahulu.")

# Introduction Page (Placeholder / Kosongkan atau Tambahkan Sesuai Keinginan)
if page == "Introduction":
    st.title("Selamat Datang di Capital Bikeshare Dashboard")
    st.write("""
        Aplikasi ini menyajikan dashboard interaktif untuk menganalisis data penggunaan layanan Capital Bikeshare.
        Silakan navigasi ke **Dashboard** untuk melihat visualisasi data.
    """)

st.caption("Dibuat oleh Talitha Shakira")
