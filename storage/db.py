import os

import psycopg2

try:
    import config
except ImportError:
    raise SystemExit("config.py introuvable : copie config.example.py en config.py et remplis-le")


def log_error(message):
    """Ajoute une ligne d'erreur dans logs/storage.log"""
    os.makedirs('logs', exist_ok=True)
    with open('logs/storage.log', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def get_connection():
    """Ouvre la connexion à la base PostgreSQL (paramètres lus dans config.py)."""
    try:
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
    except psycopg2.Error as e:
        log_error(f"get_connection : connexion impossible : {e}")
        raise
