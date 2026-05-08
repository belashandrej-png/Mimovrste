# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide", page_icon="📊")

st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

# Загрузка данных
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразуем цены в числовые
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None:
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{len(df):,}")
    col2.metric("📂 Категорий", df['category_name'].nunique())
    col3.metric("💰 Средняя цена", f"{df['price'].mean():.2f} €")
    col4.metric("🏷️ Брендов", df['brand_name'].nunique() if 'brand_name' in df.columns else "N/A")
    
    st.markdown("---")
    
    # Графики
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Топ-10 категорий")
        top_cats = df['category_name'].value_counts().head(10).reset_index()
        top_cats.columns = ['Категория', 'Количество']
        fig1 = px.bar(top_cats, x='Количество', y='Категория', orientation='h')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_right:
        st.subheader("💰 Распределение цен")
        df_clean = df[(df['price'] > 0) & (df['price'] < 500)]
        fig2 = px.histogram(df_clean, x="price", nbins=50)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Информация о данных (исправленная версия)
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    
    # Создаем DataFrame с информацией о колонках
    info_data = {
        'Колонка': list(df.columns),
        'Тип данных': [str(dtype) for dtype in df.dtypes],
        'Заполнено (%)': [(df[col].notna().sum() / len(df) * 100).round(1) for col in df.columns],
        'Уникальных значений': [df[col].nunique() for col in df.columns]
    }
    info_df = pd.DataFrame(info_data)
    
    # Показываем как таблицу (не как st.dataframe, чтобы избежать проблем с Arrow)
    st.write(f"**Всего колонок:** {len(df.columns)}")
    st.write(f"**Всего записей:** {len(df):,}")
    st.table(info_df)
    
    # Просмотр сырых данных
    with st.expander(" Просмотр сырых данных"):
        st.dataframe(df.head(100), use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены. Проверьте путь к файлу.")
