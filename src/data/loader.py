"""
Модуль для загрузки данных
"""
import pandas as pd
import os

def load_parquet(file_path):
    """
    Загружает данные из Parquet файла.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    return pd.read_parquet(file_path)

def load_csv_chunked(file_path, chunk_size=50000):
    """
    Загружает CSV файл по чанкам.
    """
    return pd.read_csv(
        file_path, 
        sep=';', 
        chunksize=chunk_size,
        dtype='object',
        on_bad_lines='skip',
        engine='python',
        encoding='utf-8'
    )
