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
    echo Python not found - installing automatically...
    echo.
    echo Downloading Python installer (please wait)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}"
    echo.
    echo Installing Python silently...
    echo This may take 2-3 minutes...
    %TEMP%\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    timeout /t 60 >nul
    del %TEMP%\python_installer.exe
    echo Python installed successfully!
    echo.
    echo Refreshing environment...
    timeout /t 5 >nul
)
echo OK: Python ready
echo.

REM Install libraries
echo [2/6] Installing libraries...
pip install streamlit pandas plotly requests -q
echo OK: Libraries installed
echo.

REM Create folders
echo [3/6] Creating folders...
if not exist "data" mkdir data
echo OK
echo.

REM Download data
echo [4/6] Downloading data from cloud...
echo Source: https://cloud.mail.ru/public/RM8x/JTvZztfUR
echo.

python -c "import requests, os; url='https://cloud.mail.ru/public/RM8x/JTvZztfUR'; out='data/mimodump-dataset.csv'; print('Downloading...'); 
try:
 r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=30,stream=True)
 if r.status_code==200:
  with open(out,'wb') as f:
   for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
  print('OK: '+str(round(os.path.getsize(out)/1024/1024,1))+' MB')
 else: print('Failed - download manually')
except: print('Download manually: '+url)
"

if not exist "data\mimodump-dataset.csv" (
    echo.
    echo WARNING: File not found!
    echo Download from: https://cloud.mail.ru/public/RM8x/JTvZztfUR
    echo Save to: data\mimodump-dataset.csv
    timeout /t 10 >nul
)
echo.

REM Create dashboard
echo [5/6] Creating dashboard application...
(
echo import streamlit as st
echo import pandas as pd
echo import plotly.express as px
echo import os
echo st.set_page_config(layout="wide", page_title="Mimovrste")
echo st.title("Mimovrste Analytics Platform")
echo st.markdown("Price analysis and categories")
echo st.markdown("---")
echo @st.cache_data
echo def load():
echo     try:
echo         f="data/mimodump-dataset.csv"
echo         if not os.path.exists(f):
echo             st.error("File not found!")
echo             return None
echo         df=pd.read_csv(f, nrows=50000, sep=";")
echo         for c in ["price","current_price","review_count","review_stars"]:
echo             if c in df.columns: df[c]=pd.to_numeric(df[c], errors="coerce")
echo         return df
echo     except Exception as e:
echo         st.error("Error: "+str(e))
echo         return None
echo df=load()
echo if df is not None:
echo     st.success("Loaded "+str(len(df))+" items")
echo     c1,c2,c3,c4=st.columns(4)
echo     c1.metric("Items", len(df))
echo     if "brand_name" in df.columns: c2.metric("Brands", df["brand_name"].nunique())
echo     if "price" in df.columns: c3.metric("Avg Price", f"{df['price'].mean():.1f} EUR")
echo     if "review_stars" in df.columns: c4.metric("Rating", f"{df['review_stars'].mean():.2f}/5")
echo     st.markdown("---")
echo     col_a, col_b=st.columns(2)
echo     with col_a:
echo         if "category_name" in df.columns:
echo             st.subheader("Categories")
echo             cat=df["category_name"].value_counts().head(10).reset_index()
echo             cat.columns=["Category","Count"]
echo             st.plotly_chart(px.treemap(cat, path=["Category"], values="Count"), use_container_width=True)
echo     with col_b:
echo         if "price" in df.columns:
echo             st.subheader("Prices")
echo             st.plotly_chart(px.histogram(df[(df["price"]^>0)^(df["price"]^<500)], x="price"), use_container_width=True)
echo     st.markdown("---")
echo     st.subheader("Data Preview")
echo     cols=[c for c in ["name","price","brand_name","category_name"] if c in df.columns]
echo     st.dataframe(df[cols].head(50), use_container_width=True)
echo else:
echo     st.warning("No data loaded")
) > dashboard.py
echo OK: Dashboard created
echo.

REM Launch
echo [6/6] Launching dashboard...
echo.
echo ================================================
echo    Opening browser...
echo    URL: http://localhost:8501
echo ================================================
echo.
echo Keep this window open.
echo Press Ctrl+C to stop.
echo.

streamlit run dashboard.py --server.headless=true --server.enableCORS=false

pause
