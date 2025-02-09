Pour lancer mysql 
```bash
docker-compose up --build -d
```

populate la db => populate_db/populate.py regarder le .env pour changer les parametres 
sinon les données que j ai deja scrappe dans dataset

# Récupération des données

## Scraping des données depuis Allociné
Les données utilisées dans ce projet sont obtenues par scraping du site Allociné. Pour assurer une récupération structurée et efficace des informations, un script de scraping a été développé dans le fichier `populate_db/scrapper.py`.

Les principales caractéristiques du scraping sont définies dans un fichier `.env` situé dans `populate_db`, qui contient les paramètres suivants :

- **MIN_ANNEE = 2020** : Année minimale de sortie des films à récupérer.
- **MAX_ANNEE = 2025** : Année maximale de sortie des films à récupérer.
- **CHUNK_SIZE = 10** : Nombre de films scrapés en parallèle.
- **MAX_CRITIQUES = 30** : Nombre maximal de critiques récupérées par film.
  
**Le script extrait différentes informations pour chaque film, notamment :**
- Le titre du film
- L’année de sortie
- La note moyenne des critiques presse et spectateurs
- Le nombre de notes et de critiques pour chaque catégorie
- Le synopsis
- Le distributeur, la durée, la nationalité et la langue
- Les récompenses éventuelles
- Le casting (réalisateurs, scénaristes, acteurs et leurs rôles)
- Le box-office France
- Les tags associés au film

**Les critiques spectateurs avec :**
- Le pseudo de l’auteur
- La note attribuée
- La date de publication
- Le contenu de la critique
- Le nombre de mentions "utile" et "inutile" laissées par d'autres utilisateurs
  
## Constitution de la base de données MySQL
Les données extraites sont ensuite envoyées dans une base de données MySQL via l'API FastAPI (dans `app`), en passant par les endpoints de l'application. Cette base permet de stocker efficacement les films et leurs critiques tout en rendant leur requêtage rapide et flexible.

Le dossier `populate_db` contient les scripts permettant d’initialiser la base de données et d’y insérer les données collectées.

Les données sont stockées dans plusieurs tables :
- **films** : contient les informations générales sur les films
- **critiques** : contient les critiques des spectateurs
- **acteurs** : répertorie les acteurs et leurs rôles
- **realisateurs** : liste les réalisateurs des films
- **scenaristes** : regroupe les scénaristes ayant participé aux films
- **categories** : indique les genres associés aux films
- **tags** : permet de stocker les tags associés aux films

## Intéraction avec la base de données 
L’API, développée avec `FastAPI` (voir `app`), permet d'interagir avec la base de données MySQL et d'effectuer des requêtes dynamiques. Elle est constituée de plusieurs endpoints permettant de vérifier son état, d’effectuer des requêtes SQL libres et d’exécuter des requêtes d'insertion ou de mise à jour.

**Endpoints disponibles :**

### 1. Vérification du statut de l'API
- Méthode : `GET`
- URL : `/health_check`
- Description : Vérifie que l’API fonctionne correctement.

Exemple de réponse :
```json
{
"status": "success",
"message": "Health check."
}
```

### 2. Exécution de requêtes SQL de lecture
- Méthode : `POST`
- URL : `/query`
- Description : Permet d'exécuter une requête SQL et de récupérer le résultat.

Exemple de requête :
```json
{
"sql_query": "SELECT * FROM films WHERE annee >= 2020;"
}
```

### 3. Exécution de requêtes SQL d'écriture
- Méthode : `POST`
- URL : `/execution`
- Description : Permet d'exécuter une requête SQL de modification (insertion, mise à jour, suppression).

Exemple de requête :
```json
{
"sql_query": "INSERT INTO critiques (film_id, critique, note) VALUES (1, 'Très bon film', 4.5);"
}
```

L'API repose sur une classe `MySQLManager` qui assure la connexion à la base de données et l'exécution sécurisée des requêtes.
