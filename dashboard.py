# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide", page_icon="📊")
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
        
        # Преобразуем числовые поля
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
    
    if 'category_name' in df.columns:
        col2.metric("📂 Категорий", df['category_name'].nunique())
    else:
        col2.metric("📂 Категорий", "N/A")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col3.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    # ✅ ИСПРАВЛЕНИЕ: Правильный подсчёт брендов
    if 'brand_name' in df.columns:
        # Удаляем пустые, NaN и строки с пробелами
        brands = df['brand_name'].dropna()
        brands = brands[brands.astype(str).str.strip() != '']
        brands = brands[brands.astype(str).str.strip().str.lower() != 'unknown']
        brands_count = brands.nunique()
        col4.metric("🏷️ Брендов", f"{brands_count:,}" if brands_count > 0 else "N/A")
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
            fig = px.bar(top_cats, x='Количество', y='Категория', orientation='h',
                        color='Количество', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            valid = df[df['price'].between(0, 500)]['price'].dropna()
            if len(valid) > 0:
                fig = px.histogram(valid, x="price", nbins=50,
                                 color_discrete_sequence=['#1f77b4'])
                st.plotly_chart(fig, use_container_width=True)
    
    # Доп. аналитика
    st.markdown("---")
    st.subheader("📊 Топ-10 брендов по количеству товаров")
    if 'brand_name' in df.columns:
        top_brands = df['brand_name'].dropna()
        top_brands = top_brands[top_brands.astype(str).str.strip() != '']
        top_brands = top_brands.value_counts().head(10).reset_index()
        top_brands.columns = ['Бренд', 'Количество']
        fig_brands = px.bar(top_brands, x='Количество', y='Бренд', orientation='h',
                           color='Количество', color_continuous_scale='Greens')
        st.plotly_chart(fig_brands, use_container_width=True)
    
    # Информация о данных
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    info = []
    for col in df.columns:
        non_null = df[col].notna().sum()
        info.append({
            'Колонка': col,
            'Тип': str(df[col].dtype),
            'Заполнено (%)': f"{(non_null / len(df) * 100):.1f}",
            'Уникальных': df[col].nunique()
        })
    info_df = pd.DataFrame(info)
    st.table(info_df)
    
    # Просмотр данных
    with st.expander("🔍 Просмотр первых 100 записей"):
        st.dataframe(df.head(100), use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены. Проверьте путь к файлу.")

# Футер
st.markdown("---")
st.markdown("*Аналитическая платформа Mimovrste © 2026*")
