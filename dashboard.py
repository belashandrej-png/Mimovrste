import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mimovrste Analytics", layout="wide", page_icon="📊")

st.title("💎 Аналитическая Платформа Mimovrste PRO")
st.markdown("Глубокий анализ динамики цен, брендов и категорий товаров")
st.markdown("---")

@st.cache_data(ttl=3600)
def load_data():
    try:
        # Пробуем разные разделители
        for sep in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(
                    'O:/extracted/mimodump-dataset.csv',
                    nrows=50000,
                    sep=sep,
                    low_memory=False,
                    encoding='utf-8'
                )
                # Если прочитали больше 1 колонки — разделитель правильный
                if len(df.columns) > 1:
                    break
            except:
                continue
        
        # Преобразуем числовые колонки
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
    st.success(f"✅ Загружено {len(df):,} строк")
    
    # Показываем первые строки для отладки
    st.write("📋 Доступные колонки:", list(df.columns))
    
    # Боковая панель
    st.sidebar.header("⚙️ Фильтры")
    
    # KPI метрики
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Всего строк", f"{len(df):,}")
    
    if 'price' in df.columns:
        col2.metric("💰 Средняя цена", f"{df['price'].mean():.2f} €")
    
    if 'brand_name' in df.columns:
        col3.metric("🏷️ Брендов", df['brand_name'].nunique())
    
    st.markdown("---")
    
    # Графики (если есть нужные колонки)
    if 'price' in df.columns:
        st.subheader("💸 Распределение цен")
        df_clean = df[df['price'].notna()]
        fig = px.histogram(df_clean, x='price', nbins=50)
        st.plotly_chart(fig, use_container_width=True)
    
    # Показываем таблицу
    st.subheader("📊 Данные (первые 10 строк)")
    st.dataframe(df.head(10))

else:
    st.warning("⚠️ Данные не загружены")
