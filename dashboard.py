# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === НАСТРОЙКИ СТРАНИЦЫ И ТЕМЫ ===
st.set_page_config(page_title="Mimovrste PRO Analytics", layout="wide", page_icon="📊")

# Кастомный CSS для красивого дизайна (ГОЛУБАЯ ТЕМА)
st.markdown("""
<style>
    /* Основной фон и шрифты */
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #0074D9 50%, #7FDBFF 100%);
        color: #ffffff;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #e0f7ff !important;
        text-shadow: 2px 2px 4px #000000;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Боковая панель */
    .css-1d391kg, .css-1l02zno {
        background-color: #001f3f !important;
    }
    
    /* Стиль метрик */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #7FDBFF !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #b3e0ff !important;
    }

    /* Карточки (имитация) */
    .metric-card {
        background: rgba(0, 116, 217, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(127, 219, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 116, 217, 0.5);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: scale(1.02);
        border-color: #7FDBFF;
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
        
        # ИСПРАВЛЕНИЕ: Преобразуем review_stars к числовому типу
        if 'review_stars' in df.columns:
            df['review_stars'] = pd.to_numeric(df['review_stars'], errors='coerce')
        
        if 'review_count' in df.columns:
            df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')
        
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
        # ИСПРАВЛЕНИЕ: явно преобразуем все значения к float
        min_price = float(df['price'].min()) if not df['price'].isna().all() else 0.0
        max_price = float(df['price'].max()) if not df['price'].isna().all() else 1000.0
        
        # Убеждаемся, что значение по умолчанию тоже float
        default_max = float(min(max_price, 500.0))
        
        price_range = st.sidebar.slider(
            "Диапазон цен (€):",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, default_max)
        )
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]

    # === БЛОК 1: KPI МЕТРИКИ (Красивые карточки) ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📦 Всего Товаров", value=f"{len(df):,}", delta_color="off")
    
    with col2:
        if 'brand_name' in df.columns:
            st.metric(label="🏷️ Уникальных Брендов", value=f"{df['brand_name'].nunique():,}")
        else:
            st.metric(label="🏷️ Уникальных Брендов", value="N/A")
    
    with col3:
        if 'price' in df.columns:
            valid_prices = df['price'].dropna()
            st.metric(label="💰 Средняя Цена", value=f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    
    with col4:
        if 'review_stars' in df.columns:
            valid_ratings = df['review_stars'].dropna()
            st.metric(label="⭐ Средний Рейтинг", value=f"{valid_ratings.mean():.2f}/5" if len(valid_ratings) > 0 else "N/A")
        else:
            st.metric(label="⭐ Средний Рейтинг", value="N/A")

    st.markdown("---")

    # === БЛОК 2: ГРАФИКИ ВЕРХНЕГО УРОВНЯ ===
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Структура Категорий (Treemap)")
        if 'category_name' in df.columns:
            cat_counts = df['category_name'].value_counts().head(15).reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig_tree = px.treemap(cat_counts, path=['Категория'], values='Количество',
                                  color='Количество', color_continuous_scale='Blues',
                                  title='Топ-15 категорий по объему')
            fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_b:
        st.subheader("💸 Распределение цен (Histogram)")
        if 'price' in df.columns:
            df_clean = df[(df['price'] > 0) & (df['price'] < 500)]
            fig_hist = px.histogram(df_clean, x='price', nbins=50, 
                                    color_discrete_sequence=['#0074D9'], # Голубой цвет
                                    title='Частота встречаемости цен')
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font_color="white")
            st.plotly_chart(fig_hist, use_container_width=True)

    # === БЛОК 3: ДЕТАЛЬНАЯ АНАЛИТИКА (Много графиков) ===
    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")
    
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🏆 Топ-10 Брендов (Bar Chart)")
        if 'brand_name' in df.columns:
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig_bar = px.bar(brand_counts, x='Количество', y='Бренд', orientation='h',
                             color='Количество', color_continuous_scale='Blues',
                             title='Лидеры рынка')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📉 Разброс цен по Категориям (Box Plot)")
        if 'category_name' in df.columns and 'price' in df.columns:
            # Берем топ-5 категорий для наглядности
            top_5_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_5_cats)]
            fig_box = px.box(df_box, x='category_name', y='price', color='category_name',
                             title='Медиана и выбросы цен',
                             color_discrete_sequence=px.colors.sequential.Blues)
            fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font_color="white")
            st.plotly_chart(fig_box, use_container_width=True)

    # === БЛОК 4: КОРРЕЛЯЦИИ И SCATTER ===
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💎 Цена vs Количество отзывов (Scatter)")
        if 'review_count' in df.columns and 'price' in df.columns:
            df_scatter = df[(df['review_count'] < 100) & (df['price'] < 200)].dropna() # Фильтр выбросов
            fig_scatter = px.scatter(df_scatter, x='review_count', y='price',
                                     color='category_name' if 'category_name' in df_scatter.columns else None, 
                                     size='price',
                                     hover_data=['name'] if 'name' in df_scatter.columns else None,
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
                                 color_continuous_scale='Blues', # Голубая гамма
                                 title='Корреляция между числовыми параметрами')
            fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   font_color="white")
            st.plotly_chart(fig_heat, use_container_width=True)

    # === БЛОК 5: ТАБЛИЦА ДАННЫХ ===
    st.markdown("---")
    st.subheader("📋 Данные (Preview)")
    
    # Показываем колонки для выбора
    available_cols = ['name', 'price', 'current_price', 'brand_name', 'category_name', 'review_stars', 'review_count']
    display_cols = [col for col in available_cols if col in df.columns]
    
    st.dataframe(df[display_cols].head(100), use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены!")
