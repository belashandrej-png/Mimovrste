@echo off
chcp 65001 >nul 2>&1
title Mimovrste Analytics - Auto Installer
color 0A

echo.
echo ================================================
echo    Mimovrste Analytics Platform
echo    Automatic Installer
echo ================================================
echo.

REM Step 1: Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python:
    echo 1. Go to: https://python.org/downloads/
    echo 2. Download Python 3.10 or higher
    echo 3. Run installer
    echo 4. CHECK "Add Python to PATH"
    echo 5. Run this file again
    echo.
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Step 2: Install packages
echo [2/6] Installing packages...
echo     Please wait 3-5 minutes...
echo.
pip install streamlit pandas plotly requests --quiet --upgrade
echo OK: Packages installed
echo.

REM Step 3: Create folders
echo [3/6] Creating folders...
if not exist "data" mkdir data
echo OK: Folders created
echo.

REM Step 4: Download data
echo [4/6] Downloading data...
echo     Source: https://cloud.mail.ru/public/RM8x/JTvZztfUR
echo.

python -c "
import requests
import os

url = 'https://cloud.mail.ru/public/RM8x/JTvZztfUR'
output = 'data/mimodump-dataset.csv'

print('Downloading data...')
print('If this fails, download manually:')
print('1. Open: ' + url)
print('2. Click Download button')
print('3. Save as: data/mimodump-dataset.csv')
print()

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=30, stream=True)
    if r.status_code == 200:
        with open(output, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(output) / (1024*1024)
        print('OK: Downloaded ' + str(round(size, 1)) + ' MB')
    else:
        print('HTTP Error: ' + str(r.status_code))
except Exception as e:
    print('Download failed: ' + str(e))
"

if not exist "data\mimodump-dataset.csv" (
    echo.
    echo WARNING: File not found!
    echo Download manually from:
    echo https://cloud.mail.ru/public/RM8x/JTvZztfUR
    echo Save to: data/mimodump-dataset.csv
    echo.
    timeout /t 10 >nul
)
echo.

REM Step 5: Create dashboard
echo [5/6] Creating dashboard...

(
echo import streamlit as st
echo import pandas as pd
echo import plotly.express as px
echo import os
echo.
echo st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="📊")
echo.
echo st.markdown("""
echo ^<style^>
echo     .stApp { background-color: #FFFFFF !important; }
echo     h1, h2, h3, p, div, label { color: #1e3a8a !important; }
echo     .stSidebar { background-color: #f8fafc !important; }
echo     div[data-testid="stMetric"] {
echo         background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%) !important;
echo         padding: 15px !important; border-radius: 10px !important;
echo     }
echo     div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
echo     div[data-testid="stMetricLabel"] { color: #e0e7ff !important; }
echo ^</style^>
echo """, unsafe_allow_html=True)
echo.
echo st.title("💎 Mimovrste Analytics Platform")
echo st.markdown("Price analysis, brands and categories")
echo st.markdown("---")
echo.
echo @st.cache_data(ttl=3600)
echo def load_data():
echo     try:
echo         file_path = 'data/mimodump-dataset.csv'
echo         if not os.path.exists(file_path):
echo             st.error("Data file not found!")
echo             return None
echo         df = pd.read_csv(file_path, nrows=50000, sep=';', low_memory=False, encoding='utf-8')
echo         numeric_cols = ['price', 'current_price', 'review_count', 'review_stars']
echo         for col in numeric_cols:
echo             if col in df.columns:
echo                 df[col] = pd.to_numeric(df[col], errors='coerce')
echo         return df
echo     except Exception as e:
echo         st.error(f"Error: {e}")
echo         return None
echo.
echo df = load_data()
echo.
echo if df is not None:
echo     st.success(f"Loaded {len(df):,} items")
echo     st.sidebar.header("Filters")
echo     if 'brand_name' in df.columns:
echo         brands = df['brand_name'].value_counts().head(20).index
echo         selected = st.sidebar.multiselect("Brands:", options=brands, default=list(brands[:5]))
echo         if selected: df = df[df['brand_name'].isin(selected)]
echo     if 'price' in df.columns:
echo         valid = df['price'].dropna()
echo         if len(valid) ^> 0:
echo             rng = st.sidebar.slider("Price range:", min_value=float(valid.min()), max_value=float(valid.max()), value=(float(valid.min()), min(float(valid.max()), 500.0)))
echo             df = df[(df['price'] ^= rng[0]) ^& (df['price'] ^= rng[1])]
echo     c1,c2,c3,c4 = st.columns(4)
echo     c1.metric("Items", f"{len(df):,}")
echo     if 'brand_name' in df.columns: c2.metric("Brands", df['brand_name'].nunique())
echo     if 'price' in df.columns: c3.metric("Avg Price", f"{df['price'].mean():.2f} EUR")
echo     if 'review_stars' in df.columns: c4.metric("Rating", f"{df['review_stars'].mean():.2f}/5")
echo     st.markdown("---")
echo     col_a, col_b = st.columns(2)
echo     with col_a:
echo         if 'category_name' in df.columns:
echo             st.subheader("Categories")
echo             cat = df['category_name'].value_counts().head(15).reset_index()
echo             cat.columns = ['Category', 'Count']
echo             fig = px.treemap(cat, path=['Category'], values='Count', color='Count', color_continuous_scale='Viridis')
echo             st.plotly_chart(fig, use_container_width=True)
echo     with col_b:
echo         if 'price' in df.columns:
echo             st.subheader("Price Distribution")
echo             df_clean = df[(df['price']^>0) ^& (df['price']^<500)].dropna(subset=['price'])
echo             fig = px.histogram(df_clean, x='price', nbins=50, color_discrete_sequence=['#FF6B6B'])
echo             st.plotly_chart(fig, use_container_width=True)
echo     st.markdown("---")
echo     st.subheader("Details")
echo     c1, c2 = st.columns(2)
echo     with c1:
echo         if 'brand_name' in df.columns:
echo             st.subheader("Top Brands")
echo             bc = df['brand_name'].value_counts().head(10).reset_index()
echo             bc.columns = ['Brand', 'Count']
echo             fig = px.bar(bc, x='Count', y='Brand', orientation='h', color='Count', color_continuous_scale='Rainbow')
echo             st.plotly_chart(fig, use_container_width=True)
echo     with c2:
echo         if 'category_name' in df.columns and 'price' in df.columns:
echo             st.subheader("Prices by Category")
echo             top = df['category_name'].value_counts().head(5).index
echo             df_box = df[df['category_name'].isin(top)].dropna(subset=['price'])
echo             fig = px.box(df_box, x='category_name', y='price', color='category_name')
echo             st.plotly_chart(fig, use_container_width=True)
echo     st.markdown("---")
echo     st.subheader("Data Preview")
echo     cols = [c for c in ['name','price','brand_name','category_name'] if c in df.columns]
echo     st.dataframe(df[cols].head(50), use_container_width=True)
echo else:
echo     st.warning("No data loaded")
) > dashboard.py

echo OK: Dashboard created
echo.

REM Step 6: Launch
echo [6/6] Launching dashboard...
echo.
echo ================================================
echo    Opening browser...
echo    URL: http://localhost:8501
echo ================================================
echo.
echo Keep this window open.
echo To stop: Press Ctrl+C
echo.

streamlit run dashboard.py --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false

pause
