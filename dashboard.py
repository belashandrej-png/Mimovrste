# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Настройка страницы
st.set_page_config(page_title="Mimovrste Analytics Pro", layout="wide", page_icon="📊")

# Стили CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Продвинутый анализ динамики цен и структуры ассортимента*")
st.markdown("---")

# ===== БОКОВАЯ ПАНЕЛЬ =====
st.sidebar.header("🎨 Настройки")

# Выбор цветовой темы
color_theme = st.sidebar.selectbox(
    "Цветовая схема:",
    ["Blues", "Greens", "Purples", "Oranges", "Reds", "Viridis", "Plasma"],
    index=0
)

st.sidebar.header("🔍 Фильтры")

# Загрузка данных
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразуем цены
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Преобразуем числовые поля
        for col in ['review_count', 'review_stars']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Преобразуем дату если есть
        if 'parsed_at' in df.columns:
            df['parsed_at'] = pd.to_datetime(df['parsed_at'], errors='coerce')
            df['date'] = df['parsed_at'].dt.date
            df['month'] = df['parsed_at'].dt.to_period('M')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None and len(df) > 0:
    # ===== ФИЛЬТРЫ =====
    if 'category_name' in df.columns:
        categories = sorted(df['category_name'].dropna().unique())
        selected_categories = st.sidebar.multiselect(
            "Категории:",
            options=categories,
            default=categories[:10] if len(categories) > 10 else categories
        )
        if selected_categories:
            df = df[df['category_name'].isin(selected_categories)]
    
    if 'brand_name' in df.columns:
        brands = sorted(df['brand_name'].dropna().unique())
        selected_brands = st.sidebar.multiselect(
            "Бренды:",
            options=brands,
            default=brands[:20] if len(brands) > 20 else brands
        )
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]
    
    if 'price' in df.columns:
        min_price = float(df['price'].min()) if not df['price'].isna().all() else 0
        max_price = float(df['price'].max()) if not df['price'].isna().all() else 1000
        price_range = st.sidebar.slider(
            "Диапазон цен (€):",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, min(max_price, 500))
        )
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
    
    # ===== МЕТРИКИ =====
    st.subheader("📈 Основные показатели")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("📦 Товаров", f"{len(df):,}")
    
    if 'category_name' in df.columns:
        col2.metric("📂 Категорий", f"{df['category_name'].nunique():,}")
    
    if 'brand_name' in df.columns:
        brands_count = df['brand_name'].dropna().nunique()
        col3.metric("🏷️ Брендов", f"{brands_count:,}")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col4.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    
    if 'review_stars' in df.columns:
        avg_rating = df['review_stars'].mean()
        col5.metric("⭐ Средний рейтинг", f"{avg_rating:.1f}/5" if not pd.isna(avg_rating) else "N/A")
    
    st.markdown("---")
    
    # ===== ГРАФИКИ 1 =====
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Treemap категорий")
        if 'category_name' in df.columns:
            cat_counts = df['category_name'].value_counts().reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig_treemap = px.treemap(
                cat_counts, 
                path=['Категория'], 
                values='Количество',
                color='Количество',
                color_continuous_scale=color_theme
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            valid = df[df['price'].between(0, 500)]['price'].dropna()
            if len(valid) > 0:
                fig_hist = px.histogram(valid, x="price", nbins=50)
                st.plotly_chart(fig_hist, use_container_width=True)
    
    # ===== SCATTER PLOT: ЦЕНА VS РЕЙТИНГ =====
    st.markdown("---")
    st.subheader("🔬 Цена vs Рейтинг")
    
    if 'price' in df.columns and 'review_stars' in df.columns:
        scatter_df = df[['price', 'review_stars', 'category_name']].dropna()
        scatter_df = scatter_df[(scatter_df['price'] > 0) & (scatter_df['price'] < 500)]
        
        if len(scatter_df) > 0:
            fig_scatter = px.scatter(
                scatter_df,
                x='price',
                y='review_stars',
                color='category_name' if 'category_name' in scatter_df.columns else None,
                opacity=0.6,
                title="Распределение товаров: Цена vs Рейтинг",
                labels={'price': 'Цена (€)', 'review_stars': 'Рейтинг'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ===== HEATMAP КОРРЕЛЯЦИЙ =====
    st.markdown("---")
    st.subheader("🔥 Heatmap корреляций")
    
    numeric_cols = ['price', 'review_count', 'review_stars']
    if 'current_price' in df.columns:
        numeric_cols.append('current_price')
    if 'lowest_price' in df.columns:
        numeric_cols.append('lowest_price')
    
    numeric_df = df[numeric_cols].dropna()
    
    if len(numeric_df) > 1:
        corr_matrix = numeric_df.corr()
        
        fig_heatmap = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale=color_theme,
            title='Корреляционная матрица'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ===== ВРЕМЕННАЯ АНАЛИТИКА =====
    st.markdown("---")
    st.subheader("📅 Временная аналитика")
    
    if 'parsed_at' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Динамика появления товаров по месяцам")
            if not df['parsed_at'].isna().all():
                time_series = df.groupby(df['parsed_at'].dt.to_period('M')).size().reset_index(name='count')
                time_series['period'] = time_series['parsed_at'].astype(str)
                
                fig_time = px.line(
                    time_series,
                    x='period',
                    y='count',
                    title='Количество товаров по месяцам',
                    markers=True
                )
                st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            st.markdown("##### Динамика средней цены по месяцам")
            if 'price' in df.columns and not df['parsed_at'].isna().all():
                price_time = df.groupby(df['parsed_at'].dt.to_period('M'))['price'].mean().reset_index()
                price_time['period'] = price_time['parsed_at'].astype(str)
                
                fig_price_time = px.line(
                    price_time,
                    x='period',
                    y='price',
                    title='Средняя цена по месяцам',
                    markers=True
                )
                st.plotly_chart(fig_price_time, use_container_width=True)
    else:
        st.info("ℹ️ Временные метки (parsed_at) отсутствуют в данных")
    
    # ===== ТОП КАТЕГОРИЙ И БРЕНДОВ =====
    st.markdown("---")
    st.subheader("🏆 Топ-10")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'category_name' in df.columns:
            st.markdown("##### Топ-10 категорий")
            top_cats = df['category_name'].value_counts().head(10).reset_index()
            top_cats.columns = ['Категория', 'Количество']
            fig_cats = px.bar(
                top_cats,
                x='Количество',
                y='Категория',
                orientation='h',
                color='Количество',
                color_continuous_scale=color_theme
            )
            st.plotly_chart(fig_cats, use_container_width=True)
    
    with col2:
        if 'brand_name' in df.columns:
            st.markdown("##### Топ-10 брендов")
            top_brands = df['brand_name'].dropna().value_counts().head(10).reset_index()
            top_brands.columns = ['Бренд', 'Количество']
            fig_brands = px.bar(
                top_brands,
                x='Количество',
                y='Бренд',
                orientation='h',
                color='Количество',
                color_continuous_scale=color_theme
            )
            st.plotly_chart(fig_brands, use_container_width=True)
    
    # ===== ИНФОРМАЦИЯ О ДАННЫХ =====
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
