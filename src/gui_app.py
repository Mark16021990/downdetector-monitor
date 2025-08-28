import os
import sys

# Определяем базовый путь для ресурсов
if getattr(sys, 'frozen', False):
    # Если приложение 'заморожено' (скомпилировано)
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Добавляем путь к ресурсам
sys.path.append(base_path)