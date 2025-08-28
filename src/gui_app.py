import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import configparser
import logging
import os
import sys
from api_client import DowndetectorAPI
from notifier import Notifier

# Добавьте логирование здесь - сразу после импортов
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug("Application starting...")

# Определяем базовый путь для ресурсов
if getattr(sys, 'frozen', False):
    # Если приложение 'заморожено' (скомпилировано)
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Добавляем путь к ресурсам
sys.path.append(base_path)