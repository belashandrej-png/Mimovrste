import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройки страницы
st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="📊")

# CSS для белого фона
st.markdown("""
<style>
    /* Белый фон для всего приложения */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Тёмный текст */
    h1, h2, h3, h4, h5, h6, p, div, label, .stMarkdown {
        color: #1e3a8a !important;
    }
    
    /* Боковая панель - светло-серая */
    .stSidebar {
        background-color: #f8fafc !important;
    }
    
    /* Карточки метрик */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #e0e7ff !important;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("💎 Аналитическая Платформа Mimovrste PRO")
st.markdown("Глубокий анализ динамики цен, брендов и категорий товаров")
st.markdown("---")

# Загрузка данных
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv(
            'O:/extracted/mimodump-dataset.csv',
            nrows=50000,
            sep=';',
            low_memory=False,
            encoding='utf-8'
        )
        
        numeric_cols = ['price', 'current_price', 'lowest_price', 'msrp_price', 
                       'review_count', 'review_stars']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return None

df = load_data()

if df is not None:
    # Боковая панель
    st.sidebar.header("⚙️ Фильтры и настройки")
    
    if 'brand_name' in df.columns:
        top_brands = df['brand_name'].value_counts().head(20).index
        selected_brands = st.sidebar.multiselect(
            "Выберите бренды:", 
            options=top_brands, 
            default=list(top_brands[:5])
        )
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]

    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        if len(valid_prices) > 0:
            min_price, max_price = float(valid_prices.min()), float(valid_prices.max())
            price_range = st.sidebar.slider(
                "Диапазон цен (€):",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, min(max_price, 500.0))
            )
            df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]

    # KPI метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📦 Всего Товаров", value=f"{len(df):,}")
    with col2:
        if 'brand_name' in df.columns:
            st.metric(label="🏷️ Уникальных Брендов", value=f"{df['brand_name'].nunique():,}")
    with col3:
        if 'price' in df.columns:
            valid_prices = df['price'].dropna()
            avg_price = valid_prices.mean() if len(valid_prices) > 0 else 0
            st.metric(label="💰 Средняя Цена", value=f"{avg_price:.2f} €")
    with col4:
        if 'review_stars' in df.columns:
            valid_ratings = df['review_stars'].dropna()
            avg_rating = valid_ratings.mean() if len(valid_ratings) > 0 else 0
            st.metric(label="⭐ Средний Рейтинг", value=f"{avg_rating:.2f}/5")

    st.markdown("---")

    # ГРАФИКИ 1: Treemap и Histogram
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Структура Категорий (Treemap)")
        if 'category_name' in df.columns:
            cat_counts = df['category_name'].value_counts().head(15).reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig_tree = px.treemap(
                cat_counts, 
                path=['Категория'], 
                values='Количество',
                color='Количество', 
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_b:
        st.subheader("💸 Распределение цен (Histogram)")
        if 'price' in df.columns:
            df_clean = df[(df['price'] > 0) & (df['price'] < 500)].dropna(subset=['price'])
            if len(df_clean) > 0:
                fig_hist = px.histogram(
                    df_clean, 
                    x='price', 
                    nbins=50,
                    color_discrete_sequence=['#FF6B6B']  # Ярко-красный
                )
                st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")

    # ГРАФИКИ 2: Bar Chart и Box Plot
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🏆 Топ-10 Брендов (Bar Chart)")
        if 'brand_name' in df.columns:
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig_bar = px.bar(
                brand_counts, 
                x='Количество', 
                y='Бренд', 
                orientation='h',
                color='Количество', 
                color_continuous_scale=px.colors.sequential.Rainbow  # Радуга
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📉 Разброс цен по Категориям (Box Plot)")
        if 'category_name' in df.columns and 'price' in df.columns:
            top_5_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_5_cats)].dropna(subset=['price'])
            if len(df_box) > 0:
                fig_box = px.box(
                    df_box, 
                    x='category_name', 
                    y='price', 
                    color='category_name',
                    color_discrete_sequence=px.colors.qualitative.Pastel1  # Пастельные цвета
                )
                st.plotly_chart(fig_box, use_container_width=True)

    # ГРАФИКИ 3: Scatter и Heatmap
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💎 Цена vs Количество отзывов (Scatter)")
        if 'review_count' in df.columns and 'price' in df.columns:
            df_scatter = df[(df['review_count'] < 100) & (df['price'] < 200)].dropna(subset=['review_count', 'price'])
            if len(df_scatter) > 0:
                fig_scatter = px.scatter(
                    df_scatter, 
                    x='review_count', 
                    y='price',
                    color='category_name',
                    size='price', 
                    color_discrete_sequence=px.colors.qualitative.Set1  # Яркие цвета
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.subheader("🌡️ Тепловая карта корреляций (Heatmap)")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_heat = px.imshow(
                corr, 
                text_auto='.2f', 
                color_continuous_scale='RdBu_r'  # Красно-синий градиент
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    # Таблица с данными
    st.markdown("---")
    st.subheader("📋 Данные (Preview)")
    available_cols = ['name', 'price', 'current_price', 'brand_name', 'category_name', 'review_stars', 'review_count']
    display_cols = [col for col in available_cols if col in df.columns]
    st.dataframe(df[display_cols].head(100), use_container_width=True, height=300)

else:
    st.warning("⚠️ Данные не загружены!")
