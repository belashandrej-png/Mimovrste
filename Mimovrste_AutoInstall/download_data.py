import os
import sys
import requests
from pathlib import Path

def download_file():
    """
    Скачивает файл данных из Mail.ru Cloud
    """
    print("📥 Начинаю загрузку данных...")
    
    # Создаем папку data
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    output_path = data_dir / "mimodump-dataset.csv"
    
    # Ссылка на файл (Mail.ru Cloud)
    # Примечание: Прямая загрузка с Mail.ru Cloud может требовать авторизации
    # Если не работает - скачайте файл вручную и положите в папку data/
    
    url = "https://cloud.mail.ru/public/RM8x/JTvZztfUR"
    
    print(f"🌐 Ссылка: {url}")
    print("💡 Если автоматическая загрузка не работает:")
    print("   1. Откройте ссылку в браузере")
    print("   2. Скачайте файл mimodump-dataset.csv")
    print("   3. Положите его в папку: data/")
    print()
    
    try:
        # Пробуем скачать
        print("⏳ Загрузка началась...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Прогресс-бар
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            bar_length = 40
                            filled = int(bar_length * downloaded // total_size)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            print(f'\r   [{bar}] {percent:.1f}%', end='', flush=True)
            
            print("\n✅ Загрузка завершена!")
            
            # Проверка размера
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Размер файла: {file_size:.1f} MB")
            
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        print()
        print("=" * 50)
        print("РУЧНАЯ ЗАГРУЗКА:")
        print("=" * 50)
        print("1. Откройте в браузере:")
        print("   https://cloud.mail.ru/public/RM8x/JTvZztfUR")
        print()
        print("2. Нажмите 'Скачать'")
        print()
        print("3. Сохраните файл как:")
        print("   data/mimodump-dataset.csv")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = download_file()
    sys.exit(0 if success else 1)
