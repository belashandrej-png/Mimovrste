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
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None and len(df) > 0:
    # === МЕТРИКИ ===
    col1, col2, col3, col4 = st.columns(4)
    
    # Товаров
    col1.metric("📦 Товаров", f"{len(df):,}")
    
    # Категорий
    if 'category_name' in df.columns:
        col2.metric("📂 Категорий", f"{df['category_name'].nunique():,}")
    else:
        col2.metric("📂 Категорий", "N/A")
    
    # Средняя цена
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        avg_price = valid_prices.mean() if len(valid_prices) > 0 else 0
        col3.metric("💰 Средняя цена", f"{avg_price:.2f} €")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    # Брендов - ИСПРАВЛЕННАЯ ВЕРСИЯ
    if 'brand_name' in df.columns:
        # Удаляем NaN и пустые строки
        brands_clean = df['brand_name'].dropna()
        brands_clean = brands_clean[brands_clean.astype(str).str.strip() != '']
        brands_clean = brands_clean[brands_clean.astype(str).str.lower() != 'nan']
        brands_count = brands_clean.nunique()
        col4.metric("🏷️ Брендов", f"{brands_count:,}" if brands_count > 0 else "Нет данных")
    else:
        col4.metric("🏷️ Брендов", "N/A")
    
    st.markdown("---")
    
    # === ГРАФИКИ ===
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Топ-10 категорий по количеству товаров")
        if 'category_name' in df.columns:
            top_cats = df['category_name'].value_counts().head(10).reset_index()
            top_cats.columns = ['Категория', 'Количество']
            fig_cats = px.bar(top_cats, x='Количество', y='Категория', orientation='h',
                             color='Количество', color_continuous_scale='Blues')
            st.plotly_chart(fig_cats, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            # Фильтруем выбросы для лучшего отображения
            df_prices = df[(df['price'] > 0) & (df['price'] < df['price'].quantile(0.95))]
            if len(df_prices) > 0:
                fig_price = px.histogram(df_prices, x="price", nbins=50,
                                        color_discrete_sequence=['#1f77b4'])
                fig_price.update_layout(xaxis_title="Цена (€)", yaxis_title="Количество товаров")
                st.plotly_chart(fig_price, use_container_width=True)
    
    # === ДОПОЛНИТЕЛЬНАЯ АНАЛИТИКА ===
    st.markdown("---")
    st.subheader("📊 Дополнительная аналитика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'price' in df.columns and 'category_name' in df.columns:
            st.markdown("### 📊 Медианная цена по категориям (топ-10)")
            # Считаем медианную цену по категориям
            cat_median = df.groupby('category_name')['price'].median().sort_values(ascending=False).head(10).reset_index()
            cat_median.columns = ['Категория', 'Медианная цена (€)']
            fig_median = px.bar(cat_median, x='Медианная цена (€)', y='Категория', orientation='h',
                               color='Медианная цена (€)', color_continuous_scale='Reds')
            st.plotly_chart(fig_median, use_container_width=True)
    
    with col2:
        if 'brand_name' in df.columns:
            st.markdown("### 🏆 Топ-10 брендов")
            # Считаем топ брендов
            brands_clean = df['brand_name'].dropna()
            brands_clean = brands_clean[brands_clean.astype(str).str.strip() != '']
            if len(brands_clean) > 0:
                top_brands = brands_clean.value_counts().head(10).reset_index()
                top_brands.columns = ['Бренд', 'Количество товаров']
                fig_brands = px.bar(top_brands, x='Количество товаров', y='Бренд', orientation='h',
                                   color='Количество товаров', color_continuous_scale='Greens')
                st.plotly_chart(fig_brands, use_container_width=True)
            else:
                st.info("ℹ️ Данные о брендах отсутствуют")
    
    # === ИНФОРМАЦИЯ О ДАННЫХ ===
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    
    # Создаем таблицу с информацией о колонках
    info_data = []
    for col in df.columns:
        non_null = df[col].notna().sum()
        unique_vals = df[col].nunique()
        info_data.append({
            'Колонка': col,
            'Тип данных': str(df[col].dtype),
            'Заполнено (%)': f"{(non_null / len(df) * 100):.1f}",
            'Уникальных значений': f"{unique_vals:,}"
        })
    
    info_df = pd.DataFrame(info_data)
    st.table(info_df)
    
    # === ПРОСМОТР ДАННЫХ ===
    with st.expander("🔍 Просмотр первых 100 записей"):
        st.dataframe(df.head(100), use_container_width=True)
    
    # === СТАТИСТИКА ===
    with st.expander("📈 Статистика по числовым полям"):
        st.write(df.describe())

else:
    st.warning("⚠️ Данные не загружены. Проверьте путь к файлу: `O:\\extracted\\mimovrste_sample.parquet`")

# Футер
st.markdown("---")
st.markdown("*Аналитическая платформа Mimovrste © 2026*")
