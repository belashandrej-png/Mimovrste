# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === НАСТРОЙКИ СТРАНИЦЫ И ТЕМЫ ===
st.set_page_config(page_title="Mimovrste PRO Analytics", layout="wide", page_icon="📊")

# Кастомный CSS для красивого дизайна (Dark Purple Theme)
st.markdown("""
<style>
    /* Основной фон и шрифты */
    .stApp {
        background-color: #0f0c29;
        background-image: linear-gradient(315deg, #0f0c29 0%, #302b63 74%, #24243e 100%);
        color: #ffffff;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #e0d4fc !important;
        text-shadow: 2px 2px 4px #000000;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Боковая панель */
    .css-1d391kg, .css-1l02zno {
        background-color: #1a1a2e !important;
    }
    
    /* Стиль метрик */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #00ff88 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #b3b3b3 !important;
    }

    /* Карточки (имитация) */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: scale(1.02);
        border-color: #a855f7;
    }
    
    /* Графики */
    .js-plotly-plot .plotly .main-svg {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# === ЗАГОЛОВОК ===
st.title("💎 Аналитическая Платформа Mimovrste PRO")
st.markdown("Глубокий анализ динамики цен, брендов и категорий товаров")
st.markdown("---")

# === ЗАГРУЗКА ДАННЫХ ===
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразование типов
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None:
    
    # === БОКОВАЯ ПАНЕЛЬ ===
    st.sidebar.header("⚙️ Фильтры и настройки")
    
    # Фильтр по брендам
    if 'brand_name' in df.columns:
        brands = sorted(df['brand_name'].dropna().unique())
        # Выбираем топ-20 брендов по умолчанию, чтобы не перегружать
        top_brands = df['brand_name'].dropna().value_counts().head(20).index
        selected_brands = st.sidebar.multiselect("Выберите бренды:", options=top_brands, default=list(top_brands[:5]))
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]

    # Фильтр по цене
    if 'price' in df.columns:
        # Преобразуем к float для совместимости со слайдером
        min_price = float(df['price'].min()) if not df['price'].isna().all() else 0.0
        max_price = float(df['price'].max()) if not df['price'].isna().all() else 1000.0
        
        price_range = st.sidebar.slider(
            "Диапазон цен (€):",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, float(min(max_price, 500.0)))
        )
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]

    # === БЛОК 1: KPI МЕТРИКИ (Красивые карточки) ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📦 Всего Товаров", value=f"{len(df):,}", delta_color="off")
    with col2:
        st.metric(label="🏷️ Уникальных Брендов", value=f"{df['brand_name'].nunique():,}" if 'brand_name' in df.columns else "N/A")
    with col3:
        st.metric(label="💰 Средняя Цена", value=f"{df['price'].mean():.2f} €")
    with col4:
        st.metric(label="⭐ Средний Рейтинг", value=f"{df['review_stars'].mean():.2f}/5" if 'review_stars' in df.columns else "N/A")

    st.markdown("---")

    # === БЛОК 2: ГРАФИКИ ВЕРХНЕГО УРОВНЯ ===
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Структура Категорий (Treemap)")
        if 'category_name' in df.columns:
            cat_counts = df['category_name'].value_counts().head(15).reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig_tree = px.treemap(cat_counts, path=['Категория'], values='Количество',
                                  color='Количество', color_continuous_scale='purp',
                                  title='Топ-15 категорий по объему')
            fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_b:
        st.subheader("💸 Распределение цен (Histogram)")
        fig_hist = px.histogram(df, x='price', nbins=50, 
                                color_discrete_sequence=['#a855f7'], # Фиолетовый цвет
                                title='Частота встречаемости цен')
        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color="white")
        st.plotly_chart(fig_hist, use_container_width=True)

    # === БЛОК 3: ДЕТАЛЬНАЯ АНАЛИТИКА (Много графиков) ===
    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")
    
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(" Топ-10 Брендов (Bar Chart)")
        if 'brand_name' in df.columns:
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig_bar = px.bar(brand_counts, x='Количество', y='Бренд', orientation='h',
                             color='Количество', color_continuous_scale='plasma',
                             title='Лидеры рынка')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📉 Разброс цен по Категориям (Box Plot)")
        if 'category_name' in df.columns:
            # Берем топ-5 категорий для наглядности
            top_5_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_5_cats)]
            fig_box = px.box(df_box, x='category_name', y='price', color='category_name',
                             title='Медиана и выбросы цен',
                             color_discrete_sequence=px.colors.sequential.Purples_r)
            fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color="white")
            st.plotly_chart(fig_box, use_container_width=True)

    # === БЛОК 4: КОРРЕЛЯЦИИ И SCATTER ===
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💎 Цена vs Количество отзывов (Scatter)")
        if 'review_count' in df.columns:
            df_scatter = df[(df['review_count'] < 100) & (df['price'] < 200)].dropna() # Фильтр выбросов
            fig_scatter = px.scatter(df_scatter, x='review_count', y='price',
                                     color='category_name', size='price',
                                     hover_data=['name'],
                                     title='Зависимость цены от популярности',
                                     color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font_color="white")
            st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.subheader("🌡️ Тепловая карта корреляций (Heatmap)")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_heat = px.imshow(corr, text_auto='.2f', 
                                 color_continuous_scale='Viridis', # Фиолетово-зеленая гамма
                                 title='Корреляция между числовыми параметрами')
            fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font_color="white")
            st.plotly_chart(fig_heat, use_container_width=True)

    # === БЛОК 5: ТАБЛИЦА ДАННЫХ ===
    st.markdown("---")
    st.subheader("📋 Данные (Preview)")
    st.dataframe(df.head(10), use_container_width=True, height=300)

else:
    st.warning("⚠️ Данные не загружены!")
