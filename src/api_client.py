import requests
import json
from urllib.parse import quote

class DowndetectorAPI:
    def __init__(self, token, base_url="https://downdetector.info/api/v1"):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def make_request(self, endpoint):
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_active_alerts(self):
        return self.make_request("alerts")
    
    def get_filtered_alerts(self):
        return self.make_request("alerts/filtered")
    
    def get_service_alerts(self, service_name):
        encoded_name = quote(service_name)
        return self.make_request(f"service/{encoded_name}/alerts")
    
    def get_service_status(self, service_name):
        encoded_name = quote(service_name)
        return self.make_request(f"service/{encoded_name}/status")
    
    def get_services(self):
        return self.make_request("services")
    
    def get_branches(self):
        return self.make_request("branches")