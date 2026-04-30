"""
Модуль для анализа сезонности (Seasonality)
"""
import pandas as pd

def calculate_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Анализирует сезонность цен по месяцам.
    
    Параметры:
        df: DataFrame с колонками 'price', 'parsed_at'
    
    Возвращает:
        DataFrame с колонками ['month', 'mean_price', 'median_price', 'count', 'seasonality_index']
    """
    if 'parsed_at' not in df.columns:
        df['parsed_at'] = pd.to_datetime(df['parsed_at'], errors='coerce')
    
    df['month'] = df['parsed_at'].dt.month
    
    # Фильтруем некорректные цены
    df_clean = df[(df['price'] > 0) & (df['price'] < 10000)]
    
    # Агрегация по месяцам
    seasonality = df_clean.groupby('month')['price'].agg(
        mean_price='mean',
        median_price='median',
        count='count'
    ).reset_index()
    
    # Расчет индекса сезонности (отклонение от средней цены за весь период)
    overall_avg = seasonality['mean_price'].mean()
    seasonality['seasonality_index'] = (seasonality['mean_price'] / overall_avg * 100).round(2)
    
    return seasonality.sort_values('month')
