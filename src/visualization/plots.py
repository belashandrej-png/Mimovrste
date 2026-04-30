"""
Модуль для визуализации (Plots)
"""
import matplotlib
matplotlib.use('Agg') # Важно для работы без монитора
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

# Настройки стиля
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def save_trend_plot(df_trends: pd.DataFrame, output_path: str):
    """Рисует график динамики цен по категориям."""
    plt.figure(figsize=(14, 7))
    categories = df_trends['category_name'].unique()
    colors = plt.cm.tab10(range(len(categories)))
    
    for i, cat in enumerate(categories):
        cat_data = df_trends[df_trends['category_name'] == cat]
        plt.plot(cat_data['year'], cat_data['avg_price'], marker='o', label=cat[:20], color=colors[i])
        
    plt.title('Динамика средних цен по категориям', fontsize=14)
    plt.xlabel('Год')
    plt.ylabel('Средняя цена (евро)')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def save_seasonality_plot(df_seasonality: pd.DataFrame, output_path: str):
    """Рисует график сезонности."""
    plt.figure(figsize=(12, 6))
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    
    sns.barplot(data=df_seasonality, x='month', y='mean_price', palette='Blues_d')
    
    plt.title('Сезонность цен по месяцам', fontsize=14)
    plt.xlabel('Месяц')
    plt.ylabel('Средняя цена')
    plt.xticks(ticks=range(12), labels=months)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def save_volatility_plot(df_volatility: pd.DataFrame, output_path: str, top_n: int = 15):
    """Рисует график волатильности."""
    top_data = df_volatility.head(top_n)
    
    plt.figure(figsize=(14, 8))
    sns.barplot(data=top_data, x='cv', y='category_name', palette='Reds_r')
    
    plt.title('Топ категорий по волатильности (CV %)', fontsize=14)
    plt.xlabel('Коэффициент вариации (%)')
    plt.ylabel('Категория')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
def save_all_plots(df, trends, seasonality, volatility, output_dir):
    """Сохраняет все графики анализа в указанную директорию."""
    from pathlib import Path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Сохранение графика динамики цен...")
    save_trend_plot(trends, output_dir / "price_trend_categories.png")
    
    print("Сохранение графика сезонности...")
    save_seasonality_plot(seasonality, output_dir / "seasonality.png")
    
    print("Сохранение графика волатильности...")
    save_volatility_plot(volatility, output_dir / "volatility.png")
    
    print(f" Все графики сохранены в: {output_dir}")
