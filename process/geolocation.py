import requests
import json
import os

CACHE_FILE = "ip_cache.json"

# Le token n'est plus écrit dans ce fichier : on le lit dans config.py (optionnel)
try:
    from config import IPINFO_TOKEN as API_TOKEN
except ImportError:
    API_TOKEN = None

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            IP_CACHE = json.load(f)
    except Exception:
        IP_CACHE = {}
else:
    IP_CACHE = {}

def _log_error(message):
    os.makedirs("logs", exist_ok=True)
    with open("logs/geolocation.log", "a", encoding="utf-8") as err:
        err.write(message + "\n")

def _save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(IP_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _log_error(f"Erreur sauvegarde cache: {str(e)}")

def get_location(ip):
    if not ip or ip.startswith(('127.', '10.', '192.168.', '172.16.')):
        return {'country': 'Local', 'city': 'Local'}

    # Ila kante l-IP déjà m-sjel b success f cache (pas Unknown)
    if ip in IP_CACHE and IP_CACHE[ip].get('country') != 'Unknown':
        return IP_CACHE[ip]

    # Appel API
    try:
        url = f"https://ipinfo.io/{ip}/json"
        headers = {}
        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"

        response = requests.get(url, headers=headers, timeout=3.0)
        if response.status_code == 200:
            data = response.json()
            res = {
                'country': data.get('country', 'Unknown'),
                'city': data.get('city', 'Unknown')
            }
            # Sauvegarder f cache UNIQUEMENT si le pays est trouvé
            if res['country'] != 'Unknown':
                IP_CACHE[ip] = res
                _save_cache()
            return res

        _log_error(f"IP {ip}: ipinfo a répondu avec le code {response.status_code}")
    except Exception as e:
        _log_error(f"Erreur API IP {ip}: {str(e)}")

    return {'country': 'Unknown', 'city': 'Unknown'}
