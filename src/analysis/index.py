"""
Модуль для индексного анализа (Laspeyres Index)
"""
import pandas as pd

def calculate_laspeyres_index(df: pd.DataFrame, base_period_str: str = "2021-11") -> float:
    """
    Рассчитывает индекс цен по методу Ласпейреса.
    Формула: I = sum(p1 * q0) / sum(p0 * q0)
    
    Параметры:
        df: DataFrame с 'category_name', 'price', 'parsed_at'
        base_period_str: Строка базового периода "YYYY-MM"
    
    Возвращает:
        float: Значение индекса (например, 137.2)
    """
    if 'parsed_at' not in df.columns:
        df['parsed_at'] = pd.to_datetime(df['parsed_at'], errors='coerce')
        
    df['period'] = df['parsed_at'].dt.to_period('M')
    base_period = pd.Period(base_period_str)
    
    # 1. Базовый период
    df_base = df[df['period'] == base_period]
    if len(df_base) == 0:
        raise ValueError(f"Нет данных за базовый период {base_period_str}")
        
    # Веса (доля каждой категории в базовом периоде)
    base_weights = df_base.groupby('category_name')['price'].count()
    total_items_base = base_weights.sum()
    base_weights = base_weights / total_items_base
    
    # 2. Текущий период (берем последний доступный месяц в данных)
    current_period = df['period'].max()
    df_current = df[df['period'] == current_period]
    
    # 3. Расчет индекса
    laspeyres_val = 0.0
    categories_used = 0
    
    for cat, weight in base_weights.items():
        if cat in df_current['category_name'].values:
            p0 = df_base[df_base['category_name'] == cat]['price'].mean()
            p1 = df_current[df_current['category_name'] == cat]['price'].mean()
            
            if p0 > 0:
                laspeyres_val += (p1 / p0) * weight
                categories_used += 1
                
    return round(laspeyres_val * 100, 2)
