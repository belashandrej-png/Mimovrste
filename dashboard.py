# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Аналитическая платформа Mimovrste", layout="wide")

st.title("📊 Аналитическая платформа Mimovrste")
st.markdown("*Анализ динамики цен и структуры ассортимента*")
st.markdown("---")

# Функция загрузки данных через DuckDB (быстро и без нагрузки на память)
@st.cache_data
def load_data():
    try:
        con = duckdb.connect()
        # Читаем Parquet файл
        df = con.execute(f"SELECT * FROM 'O:\\extracted\\mimovrste_sample.parquet'").df()
        
        # Преобразуем колонки с ценами в числа (на случай если там текст)
        for col in ['price', 'current_price', 'lowest_price', 'msrp_price']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        return None

# Загружаем данные
df = load_data()

if df is not None and len(df) > 0:
    
    # --- 1. Подсчет Метрик ---
    
    # Товаров
    total_products = len(df)
    
    # Категорий
    total_categories = df['category_name'].nunique()
    
    # Средняя цена
    avg_price = df['price'].mean()
    
    # Брендов (ИСПРАВЛЕНИЕ ЗДЕСЬ)
    # .dropna() удаляет пустые клетки
    # .nunique() считает сколько УНИКАЛЬНЫХ названий осталось
    # Это посчитает так: если LEGO встречается 100 раз, это будет 1 бренд.
    if 'brand_name' in df.columns:
        total_brands = df['brand_name'].dropna().nunique()
    else:
        total_brands = 0
    
    # --- 2. Вывод метрик на экран ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Товаров", f"{total_products:,}")
    col2.metric("📂 Категорий", total_categories)
    col3.metric("💰 Средняя цена", f"{avg_price:.2f} €")
    
    # Выводим бренды. Если их 0, пишем "Нет данных", иначе число
    col4.metric("🏷️ Брендов", f"{total_brands:,}" if total_brands > 0 else "Нет данных")
    
    st.markdown("---")
    
    # --- 3. Графики ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Топ-10 категорий по количеству")
        # Считаем сколько товаров в каждой категории
        top_cats = df['category_name'].value_counts().head(10).reset_index()
        top_cats.columns = ['Категория', 'Количество']
        fig1 = px.bar(top_cats, x='Количество', y='Категория', orientation='h',
                      color='Количество', color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_right:
        st.subheader("💰 Распределение цен")
        # Фильтруем цены от 0 до 500 евро, чтобы график был красивым
        df_clean = df[(df['price'] > 0) & (df['price'] < 500)]
        fig2 = px.histogram(df_clean, x="price", nbins=50, color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig2, use_container_width=True)

    # --- 4. Дополнительная аналитика: Топ Брендов (Новое!) ---
    st.subheader("🏆 Топ-10 брендов по популярности")
    if 'brand_name' in df.columns and total_brands > 0:
        # value_counts() автоматически считает: сколько раз встречается каждое название
        # .head(10) берет топ-10
        brand_counts = df['brand_name'].value_counts().head(10).reset_index()
        brand_counts.columns = ['Бренд', 'Количество товаров']
        
        # Рисуем график
        fig_brands = px.bar(brand_counts, x='Количество товаров', y='Бренд', orientation='h',
                            color='Количество товаров', color_continuous_scale='Greens')
        st.plotly_chart(fig_brands, use_container_width=True)
    else:
        st.warning("Данные о брендах отсутствуют.")

    # --- 5. Информация о данных ---
    st.markdown("---")
    st.subheader("📋 Информация о данных")
    st.write(f"**Всего колонок:** {len(df.columns)}")
    
    # Показываем типы данных аккуратно
    data_types = pd.DataFrame(df.dtypes, columns=['Тип данных'])
    st.table(data_types)
    
    # Кнопка для просмотра сырых данных
    with st.expander("🔍 Просмотреть сырые данные (первые 100 строк)"):
        st.dataframe(df.head(100), use_container_width=True)

else:
    st.warning("⚠️ Данные не загружены. Проверьте путь к файлу.")
