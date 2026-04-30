"""
Модуль для анализа волатильности (Volatility)
"""
import pandas as pd

def calculate_volatility(df: pd.DataFrame, min_count: int = 20) -> pd.DataFrame:
    """
    Рассчитывает волатильность (коэффициент вариации) цен по категориям.
    
    Параметры:
        df: DataFrame с колонками 'category_name', 'price'
        min_count: Минимальное кол-во товаров в категории, чтобы её учитывать
    
    Возвращает:
        DataFrame с колонками ['category_name', 'mean', 'std', 'count', 'cv']
    """
    # Фильтруем цены
    df_clean = df[(df['price'] > 0) & (df['price'] < 10000)]
    
    # Группировка
    vol = df_clean.groupby('category_name')['price'].agg(
        mean='mean',
        std='std',
        count='count'
    ).reset_index()
    
    # Убираем категории с малым количеством данных
    vol = vol[vol['count'] >= min_count]
    
    # Считаем коэффициент вариации (CV)
    vol['cv'] = (vol['std'] / vol['mean'] * 100).round(2)
    
    # Сортируем по убыванию волатильности
    return vol.sort_values('cv', ascending=False)
