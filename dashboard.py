# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    .stSidebar {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("---")

# ===== БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ =====
st.sidebar.header(" Настройки")

# Выбор цветовой темы
color_theme = st.sidebar.selectbox(
    "Цветовая схема:",
    ["Blues", "Greens", "Purples", "Oranges", "Reds", "Viridis", "Plasma"],
    index=0
)

st.sidebar.header("🔍 Фильтры")

# Загрузка данных с кэшированием
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
    # ===== ФИЛЬТРЫ =====
    
    # Фильтр по категориям
    if 'category_name' in df.columns:
        categories = sorted(df['category_name'].dropna().unique())
        selected_categories = st.sidebar.multiselect(
            "Категории:",
            options=categories,
            default=categories[:10] if len(categories) > 10 else categories
        )
        if selected_categories:
            df = df[df['category_name'].isin(selected_categories)]
    
    # Фильтр по брендам
    if 'brand_name' in df.columns:
        brands = sorted(df['brand_name'].dropna().unique())
        selected_brands = st.sidebar.multiselect(
            "Бренды:",
            options=brands,
            default=brands[:20] if len(brands) > 20 else brands
        )
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]
    
    # Фильтр по цене
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
    
    # Фильтр по рейтингу
    if 'review_stars' in df.columns:
        min_rating = st.sidebar.slider("Минимальный рейтинг:", 0.0, 5.0, 0.0, 0.5)
        df = df[df['review_stars'] >= min_rating]
    
    # Поиск
    search_query = st.sidebar.text_input("🔎 Поиск товара:")
    if search_query and 'name' in df.columns:
        df = df[df['name'].str.contains(search_query, case=False, na=False)]
    
    # ===== МЕТРИКИ =====
    st.subheader("📈 Основные показатели")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📦 Товаров", f"{len(df):,}")
    
    with col2:
        if 'category_name' in df.columns:
            st.metric("📂 Категорий", f"{df['category_name'].nunique():,}")
    
    with col3:
        if 'brand_name' in df.columns:
            brands_count = df['brand_name'].dropna().nunique()
            st.metric("🏷️ Брендов", f"{brands_count:,}")
    
    with col4:
        if 'price' in df.columns:
            avg_price = df['price'].mean()
            st.metric("💰 Средняя цена", f"{avg_price:.2f} €")
    
    with col5:
        if 'review_stars' in df.columns:
            avg_rating = df['review_stars'].mean()
            st.metric("⭐ Средний рейтинг", f"{avg_rating:.1f}/5")
    
    st.markdown("---")
    
    # ===== ГРАФИКИ =====
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader(" Топ-10 категорий")
        if 'category_name' in df.columns:
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
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            valid_prices = df[df['price'] > 0]['price'].dropna()
            if len(valid_prices) > 0:
                fig_price = px.histogram(
                    valid_prices, 
                    x="price", 
                    nbins=50,
                    color_discrete_sequence=[px.colors.sequential.__dict__[color_theme][0] if hasattr(px.colors.sequential, color_theme) else '#1f77b4']
                )
                st.plotly_chart(fig_price, use_container_width=True)
    
    # ===== ДОПОЛНИТЕЛЬНАЯ АНАЛИТИКА =====
    st.markdown("---")
    st.subheader(" Расширенная аналитика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'price' in df.columns and 'category_name' in df.columns:
            st.markdown("### 📊 Средняя цена по категориям")
            cat_avg = df.groupby('category_name')['price'].median().sort_values(ascending=False).head(10).reset_index()
            cat_avg.columns = ['Категория', 'Медианная цена (€)']
            fig_avg = px.bar(
                cat_avg, 
                x='Медианная цена (€)', 
                y='Категория', 
                orientation='h',
                color='Медианная цена (€)',
                color_continuous_scale=color_theme
            )
            st.plotly_chart(fig_avg, use_container_width=True)
    
    with col2:
        if 'brand_name' in df.columns:
            st.markdown("### 🏆 Топ-10 брендов")
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
    
    # ===== ТАБЛИЦА ДАННЫХ =====
    st.markdown("---")
    st.subheader("📋 Просмотр данных")
    
    # Показываем колонки для выбора
    available_cols = ['name', 'price', 'current_price', 'brand_name', 'category_name', 'review_stars', 'review_count']
    display_cols = [col for col in available_cols if col in df.columns]
    
    st.dataframe(df[display_cols].head(100), use_container_width=True)
    
    # Статистика
    with st.expander("📊 Подробная статистика"):
        st.write(df.describe())

else:
    st.warning("⚠️ Данные не загружены")
