@echo off
title Mimovrste Auto Installer
color 0A

echo.
echo ================================================
echo    Mimovrste Analytics - Auto Installer
echo ================================================
echo.

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Installing...
    echo.
    echo Downloading Python installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'}"
    echo Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    timeout /t 30 >nul
    del python_installer.exe
    echo Python installed!
    echo.
    echo Please run this file again.
    pause
    exit /b 0
)
echo OK: Python installed
echo.

REM Install packages
echo [2/6] Installing libraries...
pip install streamlit pandas plotly requests -q
echo OK: Libraries installed
echo.

REM Create folder
echo [3/6] Creating folders...
if not exist "data" mkdir data
echo OK
echo.

REM Download data
echo [4/6] Downloading data...
echo If download fails, get file manually from:
echo https://cloud.mail.ru/public/RM8x/JTvZztfUR
echo.

python -c "import requests; import os; url='https://cloud.mail.ru/public/RM8x/JTvZztfUR'; out='data/mimodump-dataset.csv'; print('Downloading...'); 
try:
    r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=30,stream=True)
    if r.status_code==200:
        with open(out,'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        print('OK: '+str(round(os.path.getsize(out)/1024/1024,1))+' MB')
    else: print('Failed')
except: print('Download manually: '+url)
"

if not exist "data\mimodump-dataset.csv" (
    echo Download manually and save to: data\mimodump-dataset.csv
    timeout /t 5 >nul
)
echo.

REM Create dashboard
echo [5/6] Creating dashboard...
(
echo import streamlit as st
echo import pandas as pd
echo import plotly.express as px
echo import os
echo st.set_page_config(page_title="Mimovrste", layout="wide")
echo st.title("Mimovrste Analytics")
echo st.markdown("---")
echo @st.cache_data
echo def load():
echo     try:
echo         if not os.path.exists('data/mimodump-dataset.csv'):
echo             st.error("File not found!")
echo             return None
echo         df=pd.read_csv('data/mimodump-dataset.csv',nrows=50000,sep=';')
echo         for c in ['price','current_price']: 
echo             if c in df.columns: df[c]=pd.to_numeric(df[c],errors='coerce')
echo         return df
echo     except Exception as e:
echo         st.error(str(e))
echo         return None
echo df=load()
echo if df is not None:
echo     st.success(f"Loaded {len(df)} items")
echo     c1,c2,c3,c4=st.columns(4)
echo     c1.metric("Items",len(df))
echo     if 'price' in df.columns: c2.metric("Avg Price",f"{df['price'].mean():.1f} EUR")
echo     st.markdown("---")
echo     if 'category_name' in df.columns:
echo         cat=df['category_name'].value_counts().head(10).reset_index()
echo         cat.columns=['Category','Count']
echo         st.subheader("Categories")
echo         st.plotly_chart(px.treemap(cat,path=['Category'],values='Count'),use_container_width=True)
echo     if 'price' in df.columns:
echo         st.subheader("Prices")
echo         st.plotly_chart(px.histogram(df[df['price']^<500],x='price'),use_container_width=True)
echo else:
echo     st.warning("No data")
) > dashboard.py
echo OK
echo.

REM Launch
echo [6/6] Launching...
echo Opening: http://localhost:8501
echo Press Ctrl+C to stop
echo.
streamlit run dashboard.py --server.headless=true

pause
