import os
import sys

def load_config():
    config = configparser.ConfigParser()
    
    # Определяем путь к config.ini в зависимости от того,
    # запущено ли приложение как EXE или как скрипт
    if getattr(sys, 'frozen', False):
        # Если приложение запущено как EXE
        application_path = os.path.dirname(sys.executable)
    else:
        # Если приложение запущено как скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
        
    config_path = os.path.join(application_path, 'config.ini')
    config.read(config_path)
    return config