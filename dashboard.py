import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Настройки страницы
st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="💎")

# Заголовок
st.title("💎 Аналитическая Платформа Mimovrste PRO")
st.markdown("Глубокий анализ динамики цен, брендов и категорий товаров")
st.markdown("---")

# Путь к данным
DATA_PATH = "data/mimodump-dataset.csv"

@st.cache_data
def load_data():
    try:
        # Проверяем существование файла
        if not os.path.exists(DATA_PATH):
            st.error(f"❌ Файл не найден: {DATA_PATH}")
            st.info("💡 Убедитесь, что файл mimodump-dataset.csv находится в папке data/")
            return None
        
        # Загружаем данные
        df = pd.read_csv(DATA_PATH)
        
        # Преобразуем числовые колонки
        numeric_cols = ['price', 'current_price', 'lowest_price', 'msrp_price', 
                       'review_count', 'review_stars']
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
    
    # Боковая панель с фильтрами
    st.sidebar.header("⚙️ Фильтры")
    
    # Фильтр по брендам
    if 'brand_name' in df.columns:
        brands = df['brand_name'].dropna().unique()
        selected_brands = st.sidebar.multiselect(
            "Выберите бренды:", 
            brands, 
            default=list(brands[:5]) if len(brands) >= 5 else list(brands)
        )
        if selected_brands:
            df = df[df['brand_name'].isin(selected_brands)]
    
    # Фильтр по цене
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
            st.metric(label="🏷️ Брендов", value=f"{df['brand_name'].nunique():,}")
        else:
            st.metric(label="🏷️ Брендов", value="N/A")
    
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
        else:
            st.metric(label="⭐ Средний Рейтинг", value="N/A")
    
    st.markdown("---")
    
    # Графики
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
                color_continuous_scale='Blues',
                title='Топ-15 категорий'
            )
            st.plotly_chart(fig_tree, use_container_width=True)
    
    with col_b:
        st.subheader("💸 Распределение цен")
        if 'price' in df.columns:
            df_clean = df[(df['price'] > 0) & (df['price'] < 500)].dropna(subset=['price'])
            if len(df_clean) > 0:
                fig_hist = px.histogram(
                    df_clean, 
                    x='price', 
                    nbins=50,
                    color_discrete_sequence=['#3b82f6'],
                    title='Частота цен'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
    
    # Детальная аналитика
    st.markdown("---")
    st.subheader("🔍 Детальная Аналитика")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏆 Топ-10 Брендов")
        if 'brand_name' in df.columns:
            brand_counts = df['brand_name'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Бренд', 'Количество']
            fig_bar = px.bar(
                brand_counts, 
                x='Количество', 
                y='Бренд', 
                orientation='h',
                color='Количество', 
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        st.subheader("📉 Разброс цен по Категориям")
        if 'category_name' in df.columns and 'price' in df.columns:
            top_5_cats = df['category_name'].value_counts().head(5).index
            df_box = df[df['category_name'].isin(top_5_cats)].dropna(subset=['price'])
            if len(df_box) > 0:
                fig_box = px.box(
                    df_box, 
                    x='category_name', 
                    y='price', 
                    color='category_name',
                    title='Медиана и выбросы'
                )
                st.plotly_chart(fig_box, use_container_width=True)
    
    # Таблица с данными
    st.markdown("---")
    st.subheader("📋 Данные (Preview)")
    available_cols = ['name', 'price', 'current_price', 'brand_name', 'category_name', 'review_stars', 'review_count']
    display_cols = [col for col in available_cols if col in df.columns]
    st.dataframe(df[display_cols].head(100), use_container_width=True, height=300)

else:
    st.warning("⚠️ Данные не загружены!")
