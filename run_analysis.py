#!/usr/bin/env python
"""
Основной скрипт для запуска анализа Mimovrste
Запуск: python run_analysis.py
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.loader import load_parquet
from src.data.cleaner import clean_prices_df
from src.analysis.trends import calculate_price_trends
from src.analysis.seasonality import calculate_seasonality
from src.analysis.volatility import calculate_volatility
from src.analysis.index import calculate_laspeyres_index
from src.visualization.plots import save_all_plots

def main():
    print("="*70)
    print(" ЗАПУСК АНАЛИЗА MIMOVRSTE")
    print("="*70)
    
    # 1. Загрузка данных
    print("\n[1/5] Загрузка данных...")
    df = load_parquet(r"O:\extracted\mimovrste_sample.parquet")
    print(f"    Загружено {len(df):,} строк")
    
    # 2. Очистка
    print("[2/5] Очистка данных...")
    df = clean_prices_df(df)
    
    # 3. Анализ
    print("[3/5] Анализ динамики...")
    trends = calculate_price_trends(df)
    
    print("[4/5] Анализ сезонности...")
    seasonality = calculate_seasonality(df)
    
    print("[5/5] Анализ волатильности...")
    volatility = calculate_volatility(df)
    
    # 4. Визуализация
    print("\n[6/6] Генерация графиков...")
    save_all_plots(df, trends, seasonality, volatility)
    
    print("\n Анализ завершен успешно!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
