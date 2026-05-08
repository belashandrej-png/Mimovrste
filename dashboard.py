# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide")
st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразуем цены в числовые
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Преобразуем brand_name (убираем NaN)
        if 'brand_name' in df.columns:
            df['brand_name'] = df['brand_name'].fillna('Unknown')
        
        # Преобразуем другие числовые поля
        for col in ['review_count', 'review_stars', 'product_id']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None and len(df) > 0:
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", df['category_name'].nunique() if 'category_name' in df.columns else "N/A")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col3.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    if 'brand_name' in df.columns:
        brands = df['brand_name'].dropna()
        brands = brands[brands != 'Unknown']
        col4.metric("🏷️ Брендов", f"{brands.nunique():,}" if len(brands) > 0 else "N/A")
    else:
        col4.metric("🏷️ Брендов", "N/A")
    
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
    
    # Информация о данных
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    
    info = []
    for col in df.columns:
        info.append({
            'Колонка': col,
            'Тип': str(df[col].dtype),
            'Заполнено (%)': f"{(df[col].notna().sum() / len(df) * 100):.1f}",
            'Уникальных': df[col].nunique()
        })
    
    info_df = pd.DataFrame(info)
    st.table(info_df)
    
    # Просмотр данных
    with st.expander("🔍 Просмотр данных"):
        st.dataframe(df.head(100), use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены")
