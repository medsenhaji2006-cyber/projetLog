import os

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import psycopg2

from storage.db import get_connection

GRAPHS_DIR = 'serving/graphs'
TOP_N = 15          # nombre de barres affichées dans les graphiques

FAILED_BY_COUNTRY_SQL = '''
    SELECT COALESCE(country, 'inconnu') AS pays, SUM(attempts) AS tentatives
    FROM auth_logs
    WHERE event_type IN ('failed_password', 'failed_invalid_user')
    GROUP BY pays
    ORDER BY tentatives DESC
'''

SUCCESS_BY_USER_SQL = '''
    SELECT username, COUNT(*) AS connexions
    FROM auth_logs
    WHERE event_type = 'accepted'
    GROUP BY username
    ORDER BY connexions DESC
'''

FAILED_INVALID_USER_SQL = '''
    SELECT COALESCE(username, '(vide)') AS user_essaye, SUM(attempts) AS tentatives
    FROM auth_logs
    WHERE event_type = 'failed_invalid_user'
    GROUP BY user_essaye
    ORDER BY tentatives DESC
'''


def log_error(message):
    """Ajoute une ligne d'erreur dans logs/serving.log"""
    os.makedirs('logs', exist_ok=True)
    with open('logs/serving.log', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def run_query(sql):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    except psycopg2.Error as e:
        log_error(f"run_query : erreur PostgreSQL : {e}")
        raise
    finally:
        if conn:
            conn.close()


def failed_by_country():
    return run_query(FAILED_BY_COUNTRY_SQL)


def success_by_user():
    return run_query(SUCCESS_BY_USER_SQL)


def failed_invalid_user():
    return run_query(FAILED_INVALID_USER_SQL)


def top_n(rows, n=TOP_N):
    """Garde les n premières lignes et regroupe le reste dans 'Autres'."""
    if len(rows) <= n:
        return rows
    autres = sum(valeur for _, valeur in rows[n:])
    return rows[:n] + [('Autres', autres)]


def bar_chart(rows, title, xlabel, filename, color):
    """Dessine un graphique en barres horizontales et l'enregistre en PNG."""
    try:
        os.makedirs(GRAPHS_DIR, exist_ok=True)
        hauteur = max(3, 0.45 * len(rows) + 1.5)    # la figure grandit avec le nombre de barres
        fig, ax = plt.subplots(figsize=(10, hauteur))

        if rows:
            labels = [str(label) for label, _ in rows]
            values = [valeur for _, valeur in rows]
            bars = ax.barh(labels, values, color=color, height=0.6)
            ax.invert_yaxis()                      # la plus grande valeur en haut
            ax.bar_label(bars, padding=3)          # écrit la valeur au bout de chaque barre
            ax.set_xlim(0, max(values) * 1.15)     # place pour les valeurs à droite
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))   # graduations entières
            ax.set_xlabel(xlabel)
        else:
            ax.text(0.5, 0.5, "Aucune donnée dans les logs", ha='center', va='center', fontsize=14)
            ax.set_axis_off()

        ax.set_title(title)
        fig.tight_layout()
        path = os.path.join(GRAPHS_DIR, filename)
        fig.savefig(path)
        print(f"Graphique enregistré : {path}")
    except Exception as e:
        log_error(f"bar_chart ({filename}) : {e}")
        print(f"Erreur pendant le graphique {filename} : voir logs/serving.log")


def print_table(title, rows, first_col_width=15):
    print(f"\n=== {title} ===")
    if not rows:
        print("(aucune donnée)")
    for label, valeur in rows:
        print(f"{str(label):{first_col_width}} {valeur}")


def print_dashboard():
    countries = failed_by_country()
    users = success_by_user()
    invalid = failed_invalid_user()

    # Tableaux dans le terminal
    print_table("Tentatives échouées par pays", countries, 12)
    print_table("Connexions réussies par user", users)
    print_table(f"Tentatives échouées avec invalid user (top {TOP_N})", invalid[:TOP_N])

    # Graphiques matplotlib
    bar_chart(top_n(countries), "Tentatives échouées par pays",
              "Nombre de tentatives", "echecs_par_pays.png", "tab:red")
    bar_chart(users, "Connexions réussies par utilisateur",
              "Nombre de connexions", "reussites_par_user.png", "tab:green")
    bar_chart(top_n(invalid), "Tentatives échouées avec un utilisateur invalide",
              "Nombre de tentatives", "invalid_users.png", "tab:orange")

    plt.show()       # ouvre les 3 fenêtres (ferme-les pour terminer le programme)
