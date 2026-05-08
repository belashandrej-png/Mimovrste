# -*- coding: utf-8 -*-
import plotly.express as px
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
        
        # Преобразуем brand_name - заполняем пустые значения
        if 'brand_name' in df.columns:
            df['brand_name'] = df['brand_name'].fillna('Unknown')
            df['brand_name'] = df['brand_name'].astype(str)
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return None

df = load_data()

if df is not None:
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", f"{df['category_name'].nunique():,}" if 'category_name' in df.columns else "N/A")
    
    if 'price' in df.columns:
        valid_prices = df['price'].dropna()
        col3.metric("💰 Средняя цена", f"{valid_prices.mean():.2f} €" if len(valid_prices) > 0 else "N/A")
    else:
        col3.metric("💰 Средняя цена", "N/A")
    
    # ИСПРАВЛЕНИЕ: Правильный подсчет брендов
    if 'brand_name' in df.columns:
        brands = df['brand_name'].dropna()
        brands = brands[brands != 'Unknown']
        brands = brands[brands != 'nan']
        brands = brands[brands.str.strip() != '']
        brands_count = brands.nunique()
        col4.metric("🏷️ Брендов", f"{brands_count:,}" if brands_count > 0 else "N/A")
    else:
        col4.metric("🏷️ Брендов", "N/A")
    
    st.markdown("---")
    
    # Графики
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
    
    # Информация о данных (БЕЗ st.table() чтобы избежать ошибки Arrow)
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    
    # Показываем только безопасную информацию
    st.write(f"**Всего записей:** {len(df):,}")
    st.write(f"**Колонок:** {len(df.columns)}")
    st.write(f"**Имена колонок:** {', '.join(df.columns)}")
    
    # Показываем типы данных БЕЗ использования st.table()
    st.write("**Типы данных:**")
    types_text = "\n".join([f"- {col}: {dtype}" for col, dtype in df.dtypes.items()])
    st.text(types_text)
    
    # Просмотр данных с ограничением и только безопасных колонок
    with st.expander("🔍 Просмотр данных (первые 10 строк)"):
        # Выбираем только безопасные колонки (числовые и строковые)
        safe_cols = []
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                safe_cols.append(col)
            elif df[col].dtype == 'object':
                # Проверяем можно ли конвертировать
                try:
                    sample = df[col].head(10)
                    if sample.notna().all():
                        safe_cols.append(col)
                except:
                    pass
        
        if safe_cols:
            st.dataframe(df[safe_cols].head(10), use_container_width=True)
        else:
            st.write("Не удалось безопасно отобразить данные")

else:
    st.warning("⚠️ Данные не загружены")
