# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide")

st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

# Функция загрузки данных
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        # Читаем Parquet файл
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Проверяем и преобразуем цену в числовой формат
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            # Удаляем строки где цена не преобразовалась
            df = df[df['price'].notna()]
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")
        return None

# Загружаем данные
df = load_data()

if df is not None and len(df) > 0:
    st.success(f"✅ Загружено {len(df):,} записей")
    
    # Показываем метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    
    if 'category_name' in df.columns:
        col2.metric("📂 Категорий", df['category_name'].nunique())
    else:
        col2.metric("📂 Категорий", "N/A")
    
    if 'price' in df.columns and df['price'].notna().any():
        avg_price = df['price'].mean()
        col3.metric("💰 Средняя цена", f"{avg_price:.2f} €")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    if 'brand_name' in df.columns:
        col4.metric("🏷️ Брендов", df['brand_name'].nunique())
    elif 'brand' in df.columns:
        col4.metric("🏷️ Брендов", df['brand'].nunique())
    else:
        col4.metric("🏷️ Брендов", "N/A")
    
    st.markdown("---")
    
    # Показываем доступные колонки
    st.write("📋 **Доступные колонки:**", ", ".join(df.columns))
    
    # Показываем первые строки
    st.subheader("📊 Первые записи:")
    st.dataframe(df.head())
    
else:
    st.warning("⚠️ Данные не загружены или пусты. Проверьте путь к файлу.")
    st.write("Ожидаемый путь: `O:\\extracted\\mimovrste_sample.parquet`")
