"""
Модуль для очистки и подготовки данных
"""
import pandas as pd
import numpy as np

def clean_price(value):
    """
    Преобразует цену в числовой формат.
    """
    if pd.isna(value) or value == '':
        return np.nan
    
    value = str(value).strip().replace(',', '.')
    parts = value.split('.')
    
    if len(parts) > 1:
        value = parts[0] + '.' + ''.join(parts[1:])
    
    try:
        return float(value)
    except:
        return np.nan

def clean_prices_df(df, price_columns=None):
    """
    Очищает все колонки с ценами в DataFrame.
    """
    if price_columns is None:
        price_columns = ['price', 'current_price', 'lowest_price', 'msrp_price']
    
    for col in price_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_price)
    
    return df
