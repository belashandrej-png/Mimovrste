# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide")
st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

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
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None:
    # === ОТЛАДКА: Проверяем brand_name ===
    st.info("🔍 **Отладка колонки brand_name:**")
    
    if 'brand_name' in df.columns:
        total_rows = len(df)
        null_count = df['brand_name'].isna().sum()
        empty_count = (df['brand_name'] == '').sum()
        unique_count = df['brand_name'].nunique()
        non_null_count = df['brand_name'].notna().sum()
        
        col_debug1, col_debug2, col_debug3, col_debug4 = st.columns(4)
        col_debug1.metric("Всего записей", f"{total_rows:,}")
        col_debug2.metric("Пустых (NaN)", f"{null_count:,}")
        col_debug3.metric("Пустых строк", f"{empty_count:,}")
        col_debug4.metric("Уникальных значений", f"{unique_count:,}")
        
        # Показываем примеры брендов
        st.write("**Примеры брендов (первые 10 непустых):**")
        sample_brands = df['brand_name'].dropna()
        sample_brands = sample_brands[sample_brands != '']
        st.write(sample_brands.head(10).tolist())
        
        # Пробуем разные способы подсчета
        st.write("---")
        st.write("**Разные способы подсчета брендов:**")
        
        # Способ 1: Просто nunique
        method1 = df['brand_name'].nunique()
        st.write(f"1. df['brand_name'].nunique() = {method1:,}")
        
        # Способ 2: dropna + nunique
        method2 = df['brand_name'].dropna().nunique()
        st.write(f"2. df['brand_name'].dropna().nunique() = {method2:,}")
        
        # Способ 3: dropna + не пустые строки + nunique
        method3 = df['brand_name'].dropna()
        method3 = method3[method3.astype(str).str.strip() != '']
        method3 = method3.nunique()
        st.write(f"3. dropna + не пустые строки = {method3:,}")
        
        # Способ 4: groupby + count
        method4 = df.groupby('brand_name').size().reset_index(name='count')
        method4 = method4[method4['count'] > 0]
        st.write(f"4. groupby count > 0 = {len(method4):,}")
        
        # Итоговое значение для метрики
        final_brand_count = method3
        
    else:
        st.error("❌ Колонка 'brand_name' не найдена!")
        st.write("Доступные колонки:", df.columns.tolist())
        final_brand_count = 0
    
    st.markdown("---")
    
    # === МЕТРИКИ ===
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", f"{df['category_name'].nunique():,}" if 'category_name' in df.columns else "N/A")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col3.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    col4.metric("🏷️ Брендов", f"{final_brand_count:,}" if final_brand_count > 0 else "Нет данных")
    
    st.markdown("---")
    
    # === ГРАФИКИ ===
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Топ-10 категорий")
        if 'category_name' in df.columns:
            top_cats = df['category_name'].value_counts().head(10).reset_index()
            top_cats.columns = ['Категория', 'Количество']
            fig = px.bar(top_cats, x='Количество', y='Категория', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        if 'price' in df.columns:
            valid = df[df['price'].between(0, 500)]['price'].dropna()
            if len(valid) > 0:
                fig = px.histogram(valid, x="price", nbins=50)
                st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены")
