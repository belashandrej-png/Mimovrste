"""
Модуль для анализа динамики цен (Trends)
"""
import pandas as pd

def calculate_price_trends(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Рассчитывает динамику средних цен по топ-N категориям по годам.
    
    Параметры:
        df: DataFrame с колонками 'category_name', 'price', 'parsed_at'
        top_n: Количество категорий для анализа
    
    Возвращает:
        DataFrame с колонками ['year', 'category_name', 'avg_price']
    """
    # Убеждаемся, что дата преобразована
    if 'parsed_at' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['parsed_at']):
        df['parsed_at'] = pd.to_datetime(df['parsed_at'], errors='coerce')
    
    df['year'] = df['parsed_at'].dt.year
    
    # Находим топ категорий по количеству записей
    top_categories = df['category_name'].value_counts().head(top_n).index.tolist()
    
    # Фильтруем только топ категории и цены > 0
    df_filtered = df[df['category_name'].isin(top_categories) & (df['price'] > 0)]
    
    # Группировка по году и категории
    trends = df_filtered.groupby(['year', 'category_name'])['price'].mean().reset_index()
    trends.rename(columns={'price': 'avg_price'}, inplace=True)
    
    return trends
