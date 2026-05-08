# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

st.set_page_config(page_title="Mimovrste Analytics", layout="wide")
st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

DATA_PATH = r"O:\extracted\mimovrste_sample.parquet"

@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM '{DATA_PATH}'").df()
        return df
    except Exception as e:
        st.error(f" Ошибка загрузки: {e}")
        return None

df = load_data()

if df is not None:
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Товаров", f"{len(df):,}")
    col2.metric("Категорий", df['category_name'].nunique())
    col3.metric("Средняя цена", f"{df['price'].mean():.2f} €")
    col4.metric("Брендов", df['brand'].nunique())
    
    st.markdown("---")
    
    # Графики в 2 колонки
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader(" Топ-10 категорий")
        top_cats = df['category_name'].value_counts().head(10).reset_index()
        top_cats.columns = ['Категория', 'Количество']
        fig1 = px.bar(top_cats, x='Количество', y='Категория', orientation='h',
                     color='Количество', color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_right:
        st.subheader(" Распределение цен")
        df_clean = df[(df['price'] > 0) & (df['price'] < 500)]
        fig2 = px.histogram(df_clean, x="price", nbins=50, 
                           title="Гистограмма цен (0-500 €)")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Ещё графики
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader(" Цены по брендам (топ-10)")
        brand_prices = df.groupby('brand')['price'].median().sort_values(ascending=False).head(10)
        fig3 = px.bar(brand_prices, x=brand_prices.values, y=brand_prices.index,
                     orientation='h', color=brand_prices.values, color_continuous_scale='Reds')
        fig3.update_layout(xaxis_title="Медианная цена (€)")
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader(" Статистика по категориям")
        cat_stats = df.groupby('category_name')['price'].agg(['mean', 'std', 'count']).reset_index()
        cat_stats = cat_stats[cat_stats['count'] >= 100].sort_values('mean', ascending=False).head(10)
        fig4 = px.scatter(cat_stats, x='count', y='mean', size='std', 
                         hover_data=['category_name'], title="Средняя цена vs Количество товаров")
        st.plotly_chart(fig4, use_container_width=True)
    
    # Таблица данных
    with st.expander(" Просмотр сырых данных"):
        st.dataframe(df.head(100))
    
    # SQL-запросы (опционально)
    with st.expander(" SQL-запросы к данным"):
        query = st.text_area("Введите SQL-запрос:", "SELECT category_name, AVG(price) as avg_price FROM read_parquet(?) GROUP BY category_name ORDER BY avg_price DESC LIMIT 10")
        if st.button("Выполнить запрос"):
            try:
                result = duckdb.query(query.replace("?", f"'{DATA_PATH}'")).to_df()
                st.dataframe(result)
            except Exception as e:
                st.error(f"Ошибка: {e}")

else:
    st.warning(" Проверьте путь к файлу: " + DATA_PATH)
