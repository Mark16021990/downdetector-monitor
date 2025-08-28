import time
import configparser
import logging
from api_client import DowndetectorAPI
from notifier import Notifier

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("downdetector.log"),
            logging.StreamHandler()
        ]
    )
    
    # Загрузка конфигурации
    config = load_config()
    
    # Инициализация API клиента и нотификатора
    api = DowndetectorAPI(
        token=config['API']['token'],
        base_url=config['API']['base_url']
    )
    
    notifier = Notifier(
        alert_sound=config['Notifications'].getboolean('alert_sound'),
        popup_alerts=config['Notifications'].getboolean('popup_alerts')
    )
    
    poll_interval = int(config['API']['poll_interval'])
    
    logging.info("Starting Downdetector Monitor...")
    
    try:
        while True:
            # Получаем активные алерты
            alerts = api.get_filtered_alerts()
            
            if alerts and alerts.get('success'):
                notifier.process_alerts(alerts)
            else:
                logging.error("Failed to get alerts or no data received")
            
            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()