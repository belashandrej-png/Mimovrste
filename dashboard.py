# -*- coding: utf-8 -*-
import plotly.express as px
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide")
st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразуем цены
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return None

df = load_data()

if df is not None:
    # ОТЛАДКА: покажем что есть в brand_name
    if 'brand_name' in df.columns:
        st.info(f"🔍 brand_name колонка найдена!")
        st.write(f"Всего записей: {len(df)}")
        st.write(f"Пустых значений: {df['brand_name'].isna().sum()}")
        st.write(f"Непустых значений: {df['brand_name'].notna().sum()}")
        st.write(f"Уникальных брендов (всех): {df['brand_name'].nunique()}")
        st.write(f"Примеры брендов: {df['brand_name'].dropna().unique()[:5]}")
        
        # Считаем правильно
        brands_clean = df['brand_name'].dropna()
        brands_clean = brands_clean[brands_clean.astype(str).str.strip() != '']
        total_brands = brands_clean.nunique()
    else:
        st.warning("❌ Колонка brand_name НЕ найдена!")
        st.write(f"Доступные колонки: {df.columns.tolist()}")
        total_brands = 0
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", df['category_name'].nunique() if 'category_name' in df.columns else "N/A")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col3.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    col4.metric("🏷️ Брендов", f"{total_brands:,}" if total_brands > 0 else "N/A")
    
    st.markdown("---")
    
    # Графики
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Топ-10 категорий")
        if 'category_name' in df.columns:
            top_cats = df['category_name'].value_counts().head(10).reset_index()
            top_cats.columns = ['Категория', 'Количество']
            fig = px.bar(top_cats, x='Количество', y='Категория', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            valid = df[df['price'].between(0, 500)]['price'].dropna()
            if len(valid) > 0:
                fig = px.histogram(valid, x="price", nbins=50)
                st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Данные не загружены")
