# Log Analyzer - Analyse des logs d'authentification SSH

Projet de traitement et d'analyse des logs d'authentification Linux (`auth.log`), réalisé en Python avec PostgreSQL et Matplotlib.

Le pipeline lit les fichiers de logs (bruts et compressés `.gz`), extrait les informations utiles avec des expressions régulières (Regex), enrichit les adresses IP avec leur pays de provenance (API IPinfo), sauvegarde tout dans une base de données PostgreSQL, puis génère des graphiques statistiques.

---

## Architecture du projet

```text
projetLog/
├── data/                      # Fichiers de logs (auth_log.1, auth_log.2, archives .gz)
├── ingestion/
│   └── raw.py                 # Lecture des logs et décompression des fichiers .gz
├── process/
│   ├── extarct_transforme.py  # Parsing Regex (date, heure, IP, user, type d'événement)
│   └── geolocation.py         # Géolocalisation des adresses IP via IPinfo avec cache
├── storage/
│   ├── db.py                  # Connexion à la base de données PostgreSQL
│   └── save.py                # Création de la table auth_logs et insertion des données
├── serving/
│   ├── dashboard.py           # Requêtes SQL et génération des graphiques Matplotlib
│   └── graphs/                # Images des graphiques générés (.png)
└── README.md
```

---

## Les étapes du pipeline

1. **Ingestion (`ingestion/raw.py`)** :  
   Lit tous les fichiers du dossier `data/`, décompresse automatiquement les fichiers `.gz`, et ignore les fichiers en doublon. En cas d'erreur, un message est consigné dans `logs/ingestion.log`.

2. **Process (`process/`)** :  
   - `extarct_transforme.py` : Utilise des expressions régulières pour identifier le type d'événement (`failed_password`, `failed_invalid_user`, `accepted`, `session_opened`...) et extraire l'adresse IP et le nom d'utilisateur ciblé.  
   - `geolocation.py` : Interroge l'API `ipinfo.io` pour associer un pays et une ville à chaque adresse IP. Les résultats sont sauvegardés dans un cache local pour ne pas faire de requêtes répétitives.

3. **Storage (`storage/`)** :  
   - `db.py` gère la connexion à PostgreSQL via `psycopg2`.  
   - `save.py` recrée la table `auth_logs` et insère l'ensemble des enregistrements structurés à l'aide de transactions SQL (`executemany`).

4. **Serving (`serving/dashboard.py`)** :  
   Exécute les requêtes SQL d'agrégation et génère automatiquement trois graphiques dans `serving/graphs/` :
   - `echecs_par_pays.png` : Top des pays avec le plus de tentatives de connexion échouées.
   - `reussites_par_user.png` : Nombre de connexions réussies par utilisateur.
   - `invalid_users.png` : Top des noms d'utilisateurs inexistants les plus ciblés par les attaquants.

---

## Installation

1. Cloner le projet :
```bash
git clone https://github.com/medsenhaji2006-cyber/projetLog.git
cd projetLog
```

2. Installer les dépendances requises :
```bash
pip install psycopg2-binary matplotlib requests
```

---

## Configuration de la base de données

Créer un fichier `config.py` à la racine avec les identifiants de votre serveur PostgreSQL local :

```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "votre_mot_de_passe"
IPINFO_TOKEN = "votre_token_ipinfo"
```

---

## Utilisation

1. **Lancer l'ingestion, le traitement et l'insertion dans PostgreSQL :**
```bash
python -m storage.save
```

2. **Générer les graphiques d'analyse :**
```bash
python -m serving.dashboard
```
Les graphiques sont exportés sous forme d'images PNG dans le dossier `serving/graphs/`.

---

## Choix techniques & gestion des erreurs

- **Gestion des archives `.gz`** : Utilisation du module standard `gzip` pour lire directement les logs compressés sans devoir les décompresser manuellement sur le disque.
- **Cache local de géolocalisation** : Mise en cache des adresses IP déjà interrogées pour économiser le quota de l'API IPinfo et accélérer le traitement.
- **Transactions SQL** : Utilisation du gestionnaire de contexte `with conn:` pour garantir un `commit` si tout s'est bien passé ou un `rollback` automatique en cas d'erreur.
- **Logs d'erreurs dédiés** : Les erreurs d'ingestion, de stockage et de génération de graphiques sont tracées dans des fichiers de log séparés (`logs/ingestion.log`, `logs/storage.log`, etc.).

---

## Auteur

**Mohammed Senhaji**  
Groupe B - 3ème Année Ingénierie Logicielle
