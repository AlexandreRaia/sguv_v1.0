import requests
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GoogleMapsService:
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.reverse_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Converte coordenadas (lat, lng) em endereço usando a API do Google Maps
        """
        if not self.api_key:
            return None
            
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": self.api_key,
            "language": "pt-BR"
        }
        
        try:
            response = requests.get(self.reverse_geocoding_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                # Retorna o endereço formatado mais detalhado
                return data["results"][0]["formatted_address"]
            else:
                return None
                
        except requests.RequestException as e:
            print(f"Erro ao consultar Google Maps API: {e}")
            return None
    
    def get_coordinates_from_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Converte endereço em coordenadas (lat, lng) usando a API do Google Maps
        """
        if not self.api_key:
            return None
            
        params = {
            "address": address,
            "key": self.api_key,
            "language": "pt-BR"
        }
        
        try:
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return {
                    "latitude": location["lat"],
                    "longitude": location["lng"]
                }
            else:
                return None
                
        except requests.RequestException as e:
            print(f"Erro ao consultar Google Maps API: {e}")
            return None
    
    def validate_api_key(self) -> bool:
        """
        Valida se a chave da API do Google Maps está funcionando
        """
        if not self.api_key:
            return False
            
        # Testa com coordenadas conhecidas (Brasília)
        result = self.get_address_from_coordinates(-15.7942, -47.8822)
        return result is not None

# Instância global do serviço
google_maps_service = GoogleMapsService()
