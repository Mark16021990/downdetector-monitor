import json
from plyer import notification
import winsound
import logging

class Notifier:
    def __init__(self, alert_sound=True, popup_alerts=True):
        self.alert_sound = alert_sound
        self.popup_alerts = popup_alerts
        self.seen_alerts = set()
        logging.basicConfig(level=logging.INFO)
    
    def show_notification(self, title, message):
        if self.popup_alerts:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10
                )
            except Exception as e:
                logging.error(f"Failed to show notification: {e}")
        
        if self.alert_sound:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as e:
                logging.error(f"Failed to play alert sound: {e}")
        
        logging.info(f"ALERT: {title} - {message}")
    
    def process_alerts(self, alerts_data):
        if not alerts_data or 'data' not in alerts_data:
            return
        
        for alert in alerts_data['data']:
            alert_id = alert.get('id')
            if alert_id and alert_id not in self.seen_alerts:
                self.seen_alerts.add(alert_id)
                
                alert_type = alert.get('type', 'Unknown')
                service = alert.get('service', 'Unknown service')
                time = alert.get('time', '')
                
                message = f"Service: {service}\nType: {alert_type}\nTime: {time}"
                
                # Добавляем дополнительную информацию в зависимости от типа алерта
                if alert_type == 'complaints':
                    message += f"\nComplaints: {alert.get('num', 0)}"
                elif alert_type == 'url':
                    message += f"\nURL: {alert.get('url', '')}"
                elif alert_type == 'latency':
                    message += f"\nProvider: {alert.get('provider', '')}\nPlace: {alert.get('place', '')}"
                
                self.show_notification("Downdetector Alert", message)