import streamlit as st
import pandas as pd
import plotly.express as px

# === НАСТРОЙКИ СТРАНИЦЫ ===
st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="📊")

# === CSS ДЛЯ БЕЛОГО ФОНА ===
st.markdown("""
<style>
/* Принудительно белый фон для всего приложения */
.stApp {
    background-color: #FFFFFF !important;
}

/* Белый фон для основного контейнера */
.main .block-container {
    background-color: #FFFFFF !important;
}

/* Темный текст */
.stMarkdown, h1, h2, h3, h4, h5, h6, p, div, label {
    color: #1e3a8a !important;
}

/* Боковая панель - светло-серая */
.css-1d391kg, .stSidebar {
    background-color: #f8fafc !important;
}

/* Метрики - градиентные карточки */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
}

div[data-testid="stMetricValue"] {
    font-size: 2.5rem !important;
    color: #ffffff !important;
    font-weight: bold !important;
}

div[data-testid="stMetricLabel"] {
    color: #e0e7ff !important;
    font-size: 1rem !important;
}

/* Графики - прозрачный фон чтобы вписывались в белый */
.js-plotly-plot .plotly .main-svg {
    background-color: transparent !important;
}

/* Убираем синий фон по умолчанию */
.element-container, .stAlert, .stMarkdown {
    background-color: transparent !important;
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
        import duckdb
        con = duckdb.connect()
        df = con.execute("SELECT * FROM 'data/mimodump-dataset.csv'").df()
        
        numeric_cols = ['price', 'current_price', 'lowest_price', 'msrp_price', 
                       'review_count', 'review_stars']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")
        return None

df = load_data()

if df is not None:
    
    # === БОКОВАЯ ПАНЕЛЬ ===
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

    # === KPI МЕТРИКИ ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📦 Всего Товаров", value=f"{len(df):,}")
    with col2:
        if 'brand_name' in df.columns:
            st.metric(label="🏷️ Брендов", value=f"{df['brand_name'].nunique():,}")
    with col3:
        if 'price' in df.columns:
            valid_prices = df['price'].dropna()
            avg_price = valid_prices.mean() if len(valid_prices) > 0 else 0
            st.metric(label="💰 Средняя Цена", value=f"{avg_price:.2f} €")
    with col4:
        if 'review_stars' in df.columns:
            valid_ratings = df['review_stars'].dropna()
            avg_rating = valid_ratings.mean() if len(valid_ratings) > 0 else 0
            st.metric(label="⭐ Рейтинг", value=f"{avg_rating:.2f}/5")

    st.markdown("---")

    # === ГРАФИКИ ===
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Структура Категорий")
        if 'category_name' in df.columns:
            cat_counts = df['category_name'].value_counts().head(15).reset_index()
            cat_counts.columns = ['Категория', 'Количество']
            fig_tree = px.treemap(cat_counts, path=['Категория'], values='Количество',
                                  color='Количество', color_continuous_scale='Viridis')
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_b:
        st.subheader("💸 Распределение цен")
        if 'price' in df.columns:
            df_clean = df[(df['price'] > 0) & (df['price'] < 500)].dropna(subset=['price'])
            if len(df_clean) > 0:
                fig_hist = px.histogram(df_clean, x='price', nbins=50, 
                                        color_discrete_sequence=['#ff7f0e'])
                st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")
    
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🏆 Топ-10 Брендов")
        if 'brand_name' in df.columns:
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig_bar = px.bar(brand_counts, x='Количество', y='Бренд', orientation='h',
                             color='Количество', color_continuous_scale='Rainbow')
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📉 Разброс цен")
        if 'category_name' in df.columns and 'price' in df.columns:
            top_5_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_5_cats)].dropna(subset=['price'])
            if len(df_box) > 0:
                fig_box = px.box(df_box, x='category_name', y='price', color='category_name',
                                 color_discrete_sequence=px.colors.qualitative.Pastel1)
                st.plotly_chart(fig_box, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💎 Цена vs Отзывы")
        if 'review_count' in df.columns and 'price' in df.columns:
            df_scatter = df[(df['review_count'] < 100) & (df['price'] < 200)].dropna(subset=['review_count', 'price'])
            if len(df_scatter) > 0:
                fig_scatter = px.scatter(df_scatter, x='review_count', y='price',
                                         color='category_name', size='price',
                                         color_discrete_sequence=px.colors.qualitative.Set1)
                st.plotly_chart(fig_scatter, use_container_width=True)

    with c4:
        st.subheader("🌡️ Корреляции")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_heat = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Данные")
    available_cols = ['name', 'price', 'current_price', 'brand_name', 'category_name', 'review_stars', 'review_count']
    display_cols = [col for col in available_cols if col in df.columns]
    st.dataframe(df[display_cols].head(100), use_container_width=True, height=300)

else:
    st.warning("⚠️ Данные не загружены!")
