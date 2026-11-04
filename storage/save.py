import os

import psycopg2

from storage.db import get_connection, log_error

CREATE_TABLE_SQL = '''
    CREATE TABLE auth_logs (
        id         SERIAL PRIMARY KEY,
        log_month  VARCHAR(3),
        log_day    INTEGER,
        log_time   TIME,
        message    TEXT,
        ip         VARCHAR(45),
        username   VARCHAR(100),
        event_type VARCHAR(30),
        attempts   INTEGER,
        country    VARCHAR(30),
        city       VARCHAR(100)
    )
'''

INSERT_SQL = '''
    INSERT INTO auth_logs
        (log_month, log_day, log_time, message, ip, username, event_type, attempts, country, city)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''


def save_records(records):
    """Recrée la table auth_logs et y insère tous les enregistrements."""
    if not records:
        log_error("save_records : aucun enregistrement à sauvegarder")
        return

    rows = [
        (r['month'], r['day'], r['time'], r['message'], r['ip'],
         r['user'], r['event_type'], r['count'], r.get('country'), r.get('city'))
        for r in records
    ]

    conn = None
    try:
        conn = get_connection()
        with conn:                      # commit si tout va bien, rollback sinon
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS auth_logs")
                cur.execute(CREATE_TABLE_SQL)
                cur.executemany(INSERT_SQL, rows)
        print(f"{len(rows)} enregistrements sauvegardés dans auth_logs")
    except psycopg2.Error as e:
        log_error(f"save_records : erreur PostgreSQL : {e}")
        raise
    finally:
        if conn:
            conn.close()


def save_rejected(rejected, path='./storage/rejected.log'):
    """Écrit les lignes que la regex n'a pas reconnues dans un fichier."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for line in rejected:
                f.write(line + '\n')
    except OSError as e:
        log_error(f"save_rejected : impossible d'écrire {path} : {e}")
        raise
