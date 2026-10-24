#!/usr/bin/env python3
"""
🌤️ Weather Tool pour PydanticAI - OpenWeather API
Météo actuelle, prévisions (y compris demain) et comparaison de villes
"""

import os
import datetime
import requests
from typing import List, Union, Optional
from dotenv import load_dotenv

load_dotenv()

class OpenWeatherTool:
    """Outil météo utilisant l'API OpenWeather (offre gratuite)"""

    def __init__(self):
        # Accepte OPENWEATHER_API_KEY en priorité, puis GETWEATHER_API_KEY
        self.api_key = (os.getenv("OPENWEATHER_API_KEY") or os.getenv("GETWEATHER_API_KEY") or "").strip()
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def _check_api_key(self) -> Optional[str]:
        if not self.api_key:
            return "❌ OPENWEATHER_API_KEY non configurée. Veuillez ajouter votre clé OpenWeather dans le fichier .env."
        return None

    def _handle_error_response(self, response: requests.Response, city: str) -> str:
        status = response.status_code
        if status == 401:
            return (
                "❌ Clé OpenWeather invalide ou non activée (Code 401). "
                "Note : Si vous venez de générer votre clé sur openweathermap.org, l'activation peut prendre entre 10 et 30 minutes."
            )
        elif status == 404:
            return f"❌ Ville '{city}' introuvable. Vérifiez l'orthographe du nom de la ville."
        elif status == 429:
            return "❌ Limite de requêtes OpenWeather dépassée."
        else:
            return f"❌ Erreur OpenWeather ({status}) : {response.text}"

    def get_current_weather(self, city: str) -> str:
        """Obtient la météo actuelle pour une ville donnée"""
        err = self._check_api_key()
        if err:
            return err

        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city.strip(),
                "appid": self.api_key,
                "units": "metric",
                "lang": "fr"
            }
            resp = requests.get(url, params=params, timeout=12)
            if resp.status_code != 200:
                return self._handle_error_response(resp, city)

            data = resp.json()
            name = data.get("name", city)
            country = data.get("sys", {}).get("country", "")
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            temp_min = data["main"]["temp_min"]
            temp_max = data["main"]["temp_max"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data.get("wind", {}).get("speed", 0) * 3.6  # m/s to km/h
            description = data["weather"][0]["description"].capitalize()

            output = (
                f"🌍 **Météo actuelle à {name}, {country} :**\n"
                f"• Condition : {description}\n"
                f"• Température : {temp:.1f}°C (ressenti {feels_like:.1f}°C)\n"
                f"• Min / Max : {temp_min:.1f}°C / {temp_max:.1f}°C\n"
                f"• Humidité : {humidity}%\n"
                f"• Vent : {wind_speed:.1f} km/h\n"
                f"• Pression : {pressure} hPa"
            )
            return output
        except requests.exceptions.RequestException as e:
            return f"❌ Erreur réseau lors de la récupération météo : {str(e)}"
        except Exception as e:
            return f"❌ Erreur inattendue météo : {str(e)}"

    def get_forecast(self, city: str, days: int = 3) -> str:
        """
        Obtient les prévisions météo (incluant demain) via l'endpoint 5-day / 3-hour forecast
        """
        err = self._check_api_key()
        if err:
            return err

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city.strip(),
                "appid": self.api_key,
                "units": "metric",
                "lang": "fr"
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                return self._handle_error_response(resp, city)

            data = resp.json()
            city_name = data.get("city", {}).get("name", city)
            country = data.get("city", {}).get("country", "")
            items = data.get("list", [])

            if not items:
                return f"❌ Aucune prévision disponible pour '{city}'."

            # Regrouper par jour
            days_data = {}
            today_str = datetime.date.today().isoformat()
            tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

            for item in items:
                dt_txt = item["dt_txt"]  # 'YYYY-MM-DD HH:MM:SS'
                day = dt_txt.split(" ")[0]
                if day not in days_data:
                    days_data[day] = []
                days_data[day].append(item)

            output = f"📅 **Prévisions météo pour {city_name}, {country} :**\n\n"

            count = 0
            for day, entries in sorted(days_data.items()):
                if count >= max(days, 2):
                    break
                temps = [e["main"]["temp"] for e in entries]
                descriptions = [e["weather"][0]["description"] for e in entries]
                main_desc = max(set(descriptions), key=descriptions.count).capitalize()
                min_t, max_t = min(temps), max(temps)
                avg_humidity = sum(e["main"]["humidity"] for e in entries) / len(entries)

                label = day
                if day == today_str:
                    label = f"Aujourd'hui ({day})"
                elif day == tomorrow_str:
                    label = f"Demain ({day})"

                output += (
                    f"🔹 **{label} :**\n"
                    f"   • Ciel : {main_desc}\n"
                    f"   • Température : min {min_t:.1f}°C / max {max_t:.1f}°C\n"
                    f"   • Humidité moyenne : {avg_humidity:.0f}%\n\n"
                )
                count += 1

            return output.strip()
        except requests.exceptions.RequestException as e:
            return f"❌ Erreur réseau lors des prévisions météo : {str(e)}"
        except Exception as e:
            return f"❌ Erreur inattendue prévisions : {str(e)}"

    def compare_weather(self, cities: Union[List[str], str]) -> str:
        """Compare la météo entre plusieurs villes par appels séparés"""
        if isinstance(cities, str):
            city_list = [c.strip() for c in cities.replace(";", ",").replace(" et ", ",").split(",") if c.strip()]
        else:
            city_list = cities

        if not city_list:
            return "❌ Veuillez spécifier au moins deux villes à comparer."

        results = []
        for c in city_list:
            res = self.get_current_weather(c)
            results.append(res)

        output = "⚖️ **Comparaison météo :**\n\n" + "\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(results)
        return output

# Fonctions d'outils exportées pour PydanticAI
def get_weather(city: str) -> str:
    """Informations météo actuelles pour une ville"""
    return OpenWeatherTool().get_current_weather(city)

def get_weather_forecast(city: str, days: int = 3) -> str:
    """Prévisions météo pour les prochains jours (incluant demain)"""
    return OpenWeatherTool().get_forecast(city, days)

def compare_weather_tool(cities: str) -> str:
    """Compare la météo actuelle entre plusieurs villes (ex: 'Lagos, Nairobi')"""
    return OpenWeatherTool().compare_weather(cities)

if __name__ == "__main__":
    print(get_weather("Accra"))
