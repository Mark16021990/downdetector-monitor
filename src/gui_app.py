import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import configparser
import logging
import os
import sys
import json
from datetime import datetime
from api_client import DowndetectorAPI
from notifier import Notifier
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DowndetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Downdetector Monitor")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Иконка приложения (если есть)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        self.setup_gui()
        self.load_config()
        self.setup_monitoring()
        
        # Запуск периодического обновления
        self.update_interval = 5000  # 5 секунд
        self.after_id = None
        self.start_periodic_update()
    
    def setup_gui(self):
        # Создаем панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка мониторинга
        self.monitor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.monitor_frame, text="Мониторинг")
        
        # Вкладка настроек
        self.settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_frame, text="Настройки")
        
        # Вкладка статистики
        self.stats_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.stats_frame, text="Статистика")
        
        # Вкладка логов
        self.logs_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.logs_frame, text="Логи")
        
        # Настраиваем вкладку мониторинга
        self.setup_monitor_tab()
        
        # Настраиваем вкладку настроек
        self.setup_settings_tab()
        
        # Настраиваем вкладку статистики
        self.setup_stats_tab()
        
        # Настраиваем вкладку логов
        self.setup_logs_tab()
        
        # Создаем строку статуса
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_monitor_tab(self):
        # Панель управления
        control_frame = ttk.Frame(self.monitor_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Обновить", command=self.manual_update).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Начать мониторинг", command=self.start_monitoring).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Остановить", command=self.stop_monitoring).pack(side=tk.LEFT)
        
        # Индикатор состояния
        self.monitor_status = ttk.Label(control_frame, text="Остановлено", foreground="red")
        self.monitor_status.pack(side=tk.RIGHT)
        
        # Таблица с алертами
        columns = ("id", "time", "type", "service", "details")
        self.alert_tree = ttk.Treeview(self.monitor_frame, columns=columns, show="headings", height=15)
        
        # Настраиваем заголовки
        self.alert_tree.heading("id", text="ID")
        self.alert_tree.heading("time", text="Время")
        self.alert_tree.heading("type", text="Тип")
        self.alert_tree.heading("service", text="Сервис")
        self.alert_tree.heading("details", text="Детали")
        
        # Настраиваем столбцы
        self.alert_tree.column("id", width=80, anchor=tk.CENTER)
        self.alert_tree.column("time", width=150, anchor=tk.CENTER)
        self.alert_tree.column("type", width=100, anchor=tk.CENTER)
        self.alert_tree.column("service", width=200, anchor=tk.W)
        self.alert_tree.column("details", width=400, anchor=tk.W)
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(self.monitor_frame, orient=tk.VERTICAL, command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=scrollbar.set)
        
        # Упаковываем
        self.alert_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем обработчик двойного клика
        self.alert_tree.bind("<Double-1>", self.on_alert_double_click)
    
    def setup_settings_tab(self):
        # Заголовок
        ttk.Label(self.settings_frame, text="Настройки API", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Токен API
        ttk.Label(self.settings_frame, text="API Токен:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(self.settings_frame, textvariable=self.token_var, width=50, show="*")
        token_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Базовый URL
        ttk.Label(self.settings_frame, text="Базовый URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(self.settings_frame, textvariable=self.url_var, width=50).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Интервал опроса
        ttk.Label(self.settings_frame, text="Интервал опроса (сек):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar()
        ttk.Entry(self.settings_frame, textvariable=self.interval_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Настройки уведомлений
        ttk.Label(self.settings_frame, text="Уведомления", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        self.sound_var = tk.BooleanVar()
        ttk.Checkbutton(self.settings_frame, text="Звуковые уведомления", variable=self.sound_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.popup_var = tk.BooleanVar()
        ttk.Checkbutton(self.settings_frame, text="Всплывающие уведомления", variable=self.popup_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки управления настройками
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить настройки", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Загрузить настройки", command=self.load_settings_from_file).pack(side=tk.LEFT)
    
    def setup_stats_tab(self):
        # Заголовок
        ttk.Label(self.stats_frame, text="Статистика сбоев", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Фрейм для графиков
        graph_frame = ttk.Frame(self.stats_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фигуру для matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Обновляем графики
        self.update_stats()
    
    def setup_logs_tab(self):
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(self.logs_frame, width=100, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки управления логами
        button_frame = ttk.Frame(self.logs_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Обновить логи", command=self.update_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить логи", command=self.clear_logs).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Экспорт логов", command=self.export_logs).pack(side=tk.RIGHT)
    
    def load_config(self):
        try:
            logger.debug("Loading configuration...")
            self.config = configparser.ConfigParser()
            
            # Определяем путь к config.ini
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            config_path = os.path.join(application_path, 'config.ini')
            logger.debug(f"Loading config from: {config_path}")
            
            if not os.path.exists(config_path):
                logger.error(f"Config file not found at: {config_path}")
                # Создаем конфиг по умолчанию
                self.create_default_config(config_path)
                
            self.config.read(config_path)
            logger.debug("Config loaded successfully")
            
            # Заполняем поля настроек
            self.token_var.set(self.config.get('API', 'token', fallback=''))
            self.url_var.set(self.config.get('API', 'base_url', fallback='https://downdetector.info/api/v1'))
            self.interval_var.set(self.config.get('API', 'poll_interval', fallback='300'))
            self.sound_var.set(self.config.getboolean('Notifications', 'alert_sound', fallback=True))
            self.popup_var.set(self.config.getboolean('Notifications', 'popup_alerts', fallback=True))
            
            return self.config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {e}")
            return None
    
    def create_default_config(self, config_path):
        """Создает конфигурационный файл по умолчанию"""
        self.config['API'] = {
            'base_url': 'https://downdetector.info/api/v1',
            'token': 'your_token_here',
            'poll_interval': '300'
        }
        self.config['Notifications'] = {
            'alert_sound': 'True',
            'popup_alerts': 'True'
        }
        
        with open(config_path, 'w') as configfile:
            self.config.write(configfile)
        
        logger.info(f"Created default config at: {config_path}")
    
    def setup_monitoring(self):
        try:
            logger.debug("Setting up monitoring...")
            self.api = DowndetectorAPI(
                token=self.config['API']['token'],
                base_url=self.config['API']['base_url']
            )
            
            self.notifier = Notifier(
                alert_sound=self.config['Notifications'].getboolean('alert_sound'),
                popup_alerts=self.config['Notifications'].getboolean('popup_alerts')
            )
            
            self.poll_interval = int(self.config['API']['poll_interval'])
            self.monitoring = False
            self.monitor_thread = None
            logger.debug("Monitoring setup completed")
        except Exception as e:
            logger.error(f"Error setting up monitoring: {e}")
            messagebox.showerror("Ошибка", f"Не удалось настроить мониторинг: {e}")
    
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.monitor_status.config(text="Запущено", foreground="green")
            self.status_var.set("Мониторинг запущен")
            self.log("Мониторинг запущен")
    
    def stop_monitoring(self):
        self.monitoring = False
        self.monitor_status.config(text="Остановлено", foreground="red")
        self.status_var.set("Мониторинг остановлен")
        self.log("Мониторинг остановлен")
    
    def monitor_loop(self):
        while self.monitoring:
            try:
                alerts = self.api.get_filtered_alerts()
                
                if alerts and alerts.get('success'):
                    self.notifier.process_alerts(alerts)
                    self.update_alerts_table(alerts)
                    self.log(f"Проверка завершена. Найдено {len(alerts.get('data', []))} событий")
                else:
                    self.log("Не удалось получить данные или данные отсутствуют")
                
                time.sleep(self.poll_interval)
            except Exception as e:
                self.log(f"Ошибка в мониторинге: {e}")
                time.sleep(self.poll_interval)
    
    def manual_update(self):
        """Ручное обновление данных"""
        try:
            alerts = self.api.get_filtered_alerts()
            
            if alerts and alerts.get('success'):
                self.notifier.process_alerts(alerts)
                self.update_alerts_table(alerts)
                self.update_stats()
                self.log(f"Ручное обновление. Найдено {len(alerts.get('data', []))} событий")
                messagebox.showinfo("Обновление", "Данные успешно обновлены")
            else:
                self.log("Не удалось получить данные при ручном обновлении")
                messagebox.showerror("Ошибка", "Не удалось получить данные")
        except Exception as e:
            self.log(f"Ошибка при ручном обновлении: {e}")
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
    
    def update_alerts_table(self, alerts_data):
        """Обновляет таблицу с алертами"""
        # Очищаем таблицу
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        
        # Заполняем новыми данными
        if alerts_data and 'data' in alerts_data:
            for alert in alerts_data['data']:
                alert_id = alert.get('id', 'N/A')
                alert_time = alert.get('time', 'N/A')
                alert_type = alert.get('type', 'N/A')
                service = alert.get('service', 'N/A')
                
                # Формируем детали в зависимости от типа алерта
                details = ""
                if alert_type == 'complaints':
                    details = f"Жалобы: {alert.get('num', 0)}"
                elif alert_type == 'url':
                    details = f"URL: {alert.get('url', 'N/A')}"
                elif alert_type == 'latency':
                    details = f"Провайдер: {alert.get('provider', 'N/A')}, Город: {alert.get('place', 'N/A')}"
                
                # Добавляем в таблицу
                self.alert_tree.insert("", "end", values=(
                    alert_id, 
                    alert_time, 
                    alert_type, 
                    service, 
                    details
                ))
    
    def update_stats(self):
        """Обновляет графики статистики"""
        try:
            # Очищаем предыдущие графики
            self.fig.clear()
            
            # Получаем данные для графиков (здесь просто пример)
            # В реальном приложении нужно получать данные из API
            services = ['Сбербанк', 'ВТБ', 'Тинькофф', 'Госуслуги', 'Яндекс']
            incidents = [15, 8, 12, 5, 10]
            
            # Создаем график
            ax = self.fig.add_subplot(111)
            ax.bar(services, incidents)
            ax.set_title('Количество инцидентов по сервисам')
            ax.set_ylabel('Количество инцидентов')
            ax.tick_params(axis='x', rotation=45)
            
            # Обновляем canvas
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def update_logs(self):
        """Обновляет содержимое вкладки с логами"""
        try:
            log_path = "debug.log"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, content)
                self.log_text.see(tk.END)
            else:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "Файл логов не найден")
        except Exception as e:
            logger.error(f"Error updating logs: {e}")
    
    def clear_logs(self):
        """Очищает файл логов"""
        try:
            log_path = "debug.log"
            if os.path.exists(log_path):
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("")
                self.update_logs()
                self.log("Логи очищены")
        except Exception as e:
            logger.error(f"Error clearing logs: {e}")
            messagebox.showerror("Ошибка", f"Не удалось очистить логи: {e}")
    
    def export_logs(self):
        """Экспортирует логи в файл"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"Логи экспортированы в {file_path}")
                messagebox.showinfo("Успех", "Логи успешно экспортированы")
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            messagebox.showerror("Ошибка", f"Не удалось экспортировать логи: {e}")
    
    def save_settings(self):
        """Сохраняет настройки в config.ini"""
        try:
            self.config['API']['token'] = self.token_var.get()
            self.config['API']['base_url'] = self.url_var.get()
            self.config['API']['poll_interval'] = self.interval_var.get()
            self.config['Notifications']['alert_sound'] = str(self.sound_var.get())
            self.config['Notifications']['popup_alerts'] = str(self.popup_var.get())
            
            # Определяем путь к config.ini
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            config_path = os.path.join(application_path, 'config.ini')
            
            with open(config_path, 'w') as configfile:
                self.config.write(configfile)
            
            # Перезагружаем настройки
            self.setup_monitoring()
            
            self.log("Настройки сохранены")
            messagebox.showinfo("Успех", "Настройки успешно сохранены")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def load_settings_from_file(self):
        """Загружает настройки из файла"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
            )
            if file_path:
                self.config.read(file_path)
                # Обновляем поля настроек
                self.token_var.set(self.config.get('API', 'token', fallback=''))
                self.url_var.set(self.config.get('API', 'base_url', fallback='https://downdetector.info/api/v1'))
                self.interval_var.set(self.config.get('API', 'poll_interval', fallback='300'))
                self.sound_var.set(self.config.getboolean('Notifications', 'alert_sound', fallback=True))
                self.popup_var.set(self.config.getboolean('Notifications', 'popup_alerts', fallback=True))
                
                self.log(f"Настройки загружены из {file_path}")
                messagebox.showinfo("Успех", "Настройки успешно загружены")
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {e}")
    
    def on_alert_double_click(self, event):
        """Обработчик двойного клика по алерту"""
        item = self.alert_tree.selection()[0]
        values = self.alert_tree.item(item, "values")
        messagebox.showinfo("Детали алерта", f"Полная информация:\n\n{json.dumps(values, indent=2, ensure_ascii=False)}")
    
    def log(self, message):
        """Добавляет запись в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        logger.info(message)
        
        # Обновляем статус бар
        self.status_var.set(log_message)
    
    def start_periodic_update(self):
        """Запускает периодическое обновление интерфейса"""
        self.update_interface()
        self.after_id = self.root.after(self.update_interval, self.start_periodic_update)
    
    def update_interface(self):
        """Обновляет элементы интерфейса"""
        # Обновляем логи, если активна вкладка логов
        if self.notebook.index(self.notebook.select()) == 3:  # Индекс вкладки логов
            self.update_logs()
    
    def on_closing(self):
        """Обработчик закрытия приложения"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.stop_monitoring()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DowndetectorApp(root)
    
    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()