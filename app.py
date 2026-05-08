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
        # Читаем ваш parquet-файл
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        # Цены в нормальный числовой формат
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None and len(df) > 0:
    # ===== МЕТРИКИ =====
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", f"{df['category_name'].nunique():,}")
    col3.metric("💰 Средняя цена", f"{df['price'].mean():.2f} €")
    # ✅ ГЛАВНОЕ ИСПРАВЛЕНИЕ: используем brand_name, чистим пропуски
    brands_clean = df['brand_name'].dropna()          # убрали NaN
    col4.metric("🏷️ Брендов", f"{brands_clean.nunique():,}")

    st.markdown("---")

    # ===== ГРАФИКИ =====
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📈 Топ-10 категорий")
        top_cats = df['category_name'].value_counts().head(10).reset_index()
        top_cats.columns = ['Категория', 'Количество']
        fig1 = px.bar(top_cats, x='Количество', y='Категория', orientation='h')
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("💰 Распределение цен")
        valid = df[df['price'].between(0, 500)]['price'].dropna()
        fig2 = px.histogram(valid, x="price", nbins=50)
        st.plotly_chart(fig2, use_container_width=True)

    # ===== ТОП БРЕНДОВ =====
    st.subheader("🏆 Топ-10 брендов по количеству товаров")
    top_brands = brands_clean.value_counts().head(10).reset_index()
    top_brands.columns = ['Бренд', 'Количество']
    fig3 = px.bar(top_brands, x='Количество', y='Бренд', orientation='h')
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены. Проверьте путь к файлу.")
