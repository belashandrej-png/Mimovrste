import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, div, label { color: #1e3a8a !important; }
    .stSidebar { background-color: #f8fafc !important; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] { color: #e0e7ff !important; }
</style>
""", unsafe_allow_html=True)

st.title("💎 Аналитическая Платформа Mimovrste PRO")
st.markdown("Глубокий анализ динамики цен, брендов и категорий товаров")
st.markdown("---")

@st.cache_data(ttl=3600)
def load_data():
    try:
        file_path = 'data/mimodump-dataset.csv'
        
        if not os.path.exists(file_path):
            st.error("❌ Файл данных не найден! Запустите START.bat для загрузки.")
            return None
        
        df = pd.read_csv(file_path, nrows=50000, sep=';', low_memory=False, encoding='utf-8')
        
        numeric_cols = ['price', 'current_price', 'lowest_price', 'review_count', 'review_stars']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None:
    st.success(f"✅ Загружено {len(df):,} товаров")
    
    st.sidebar.header("⚙️ Фильтры")
    
    if 'brand_name' in df.columns:
        top_brands = df['brand_name'].value_counts().head(20).index
        selected_brands = st.sidebar.multiselect("Выберите бренды:", options=top_brands, default=list(top_brands[:5]))
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]

    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        if len(valid_prices) > 0:
            price_range = st.sidebar.slider("Диапазон цен (€):", min_value=float(valid_prices.min()), max_value=float(valid_prices.max()), value=(float(valid_prices.min()), min(float(valid_prices.max()), 500.0)))
            df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Всего Товаров", f"{len(df):,}")
    if 'brand_name' in df.columns:
        col2.metric("🏷️ Брендов", df['brand_name'].nunique())
    if 'price' in df.columns:
        col3.metric("💰 Средняя Цена", f"{df['price'].mean():.2f} €")
    if 'review_stars' in df.columns:
        col4.metric("⭐ Рейтинг", f"{df['review_stars'].mean():.2f}/5")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    
    with col_a:
        if 'category_name' in df.columns:
            st.subheader("📊 Структура Категорий")
            cat_counts = df['category_name'].value_counts().head(15).reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig = px.treemap(cat_counts, path=['Категория'], values='Количество', color='Количество', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if 'price' in df.columns:
            st.subheader("💸 Распределение цен")
            df_clean = df[(df['price'] > 0) & (df['price'] < 500)].dropna(subset=['price'])
            fig = px.histogram(df_clean, x='price', nbins=50, color_discrete_sequence=['#FF6B6B'])
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if 'brand_name' in df.columns:
            st.subheader("🏆 Топ Брендов")
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig = px.bar(brand_counts, x='Количество', y='Бренд', orientation='h', color='Количество', color_continuous_scale='Rainbow')
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if 'category_name' in df.columns and 'price' in df.columns:
            st.subheader("📉 Цены по категориям")
            top_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_cats)].dropna(subset=['price'])
            fig = px.box(df_box, x='category_name', y='price', color='category_name')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Данные")
    cols_to_show = ['name', 'price', 'brand_name', 'category_name']
    available_cols = [c for c in cols_to_show if c in df.columns]
    st.dataframe(df[available_cols].head(50), use_container_width=True)
