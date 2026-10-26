import gzip
import os


def log_error(message):
    """Ajoute une ligne d'erreur dans logs/ingestion.log"""
    os.makedirs('logs', exist_ok=True)
    with open('logs/ingestion.log', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def toRows(path):
    """Lit les fichiers de logs de `path` (.log et .gz) et retourne la liste des lignes."""
    try:
        files = sorted(os.listdir(path))
    except OSError as e:
        log_error(f"Impossible de lister le dossier {path} : {e}")
        raise

    rows = []
    already_read = []      # contenus déjà lus : sert à ignorer un fichier en double

    for file in files:
        file_path = path + '/' + file
        try:
            openner = gzip.open(file_path, mode='rt', encoding='utf-8', errors='replace') if file.endswith('.gz') else open(file_path, encoding='utf-8', errors='replace')
            with openner as f:
                lines = f.readlines()
        except (OSError, EOFError) as e:
            log_error(f"Lecture impossible de {file_path} : {e}")
            continue

        if lines in already_read:
            print(f"Fichier ignoré (même contenu qu'un autre fichier) : {file}")
            log_error(f"Fichier ignoré (même contenu qu'un autre fichier) : {file_path}")
            continue

        already_read.append(lines)
        rows.extend(lines)

    return rows
