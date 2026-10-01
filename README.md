# Automated Sales ETL Pipeline avec Apache Airflow & Astro CLI

[![Airflow Version](https://img.shields.io/badge/Airflow-2.x-017CEB?style=flat-square&logo=Apache%20Airflow)](https://airflow.apache.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=flat-square&logo=Python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=Docker)](https://www.docker.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)

## 📝 Présentation du Projet
Ce projet implémente un pipeline **ETL (Extract, Transform, Load)** de démonstration automatisé pour orchestrer et traiter les données de ventes d'une entreprise. Développé avec **Apache Airflow** (via l'écosystème **Astro CLI**), ce pipeline réalise l'extraction, la normalisation, la validation de la qualité des données (**Data Quality**) et le chargement final dans un entrepôt de données **PostgreSQL**.

L'objectif principal est de transformer des données brutes hétérogènes et potentiellement compromises (anomalies d'âge, montants négatifs, valeurs manquantes) en une source de vérité unique, propre et directement exploitable pour des outils de Business Intelligence (BI) ou des équipes Analytics.

---

## 📸 Aperçu du pipeline (Airflow Dashboard)
Voici le rendu visuel du pipeline ETL lorsqu'il s'exécute avec succès. Toutes les étapes (de l'extraction au chargement final dans le Data Warehouse) sont validées et au vert :

![Airflow Pipeline Success](image/capture_airflow.jpg) 

---

## 🏗️ Architecture Globale & Flux de Données
Le DAG suit quatre tâches : **Extraction → Normalisation → Contrôle qualité → Chargement**.
Les DataFrames intermédiaires sont enregistrés en Parquet sous `data/runs/<hash du run_id>/`.
XCom ne transporte que le chemin du fichier. Le CSV brut est conservé, et les montants
négatifs, les valeurs financières manquantes et les âges invalides ne sont pas corrigés
silencieusement : le contrôle qualité compte les anomalies puis bloque le lot.

Ce stockage local est adapté au `LocalExecutor` d'Astro. Pour plusieurs workers, définir
`SALES_ARTIFACT_DIR` sur un volume partagé accessible à toutes les tâches, ou adapter le
stockage à un object store. Les fichiers permettent la reprise ; leur rétention doit être
configurée avant un usage durable.

---

## 📂 Structure du Projet

Le projet suit une architecture modulaire stricte, isolant les tests d'intégration et d'orchestration dans un répertoire dédié:

```text
.
├── dags/
│   └── pipeline_sales_dags.py    # Définition et enchaînement du DAG Airflow
├── data/
│   └── sales_data.csv            # Fichier de données brutes (ignoré par Git)
├── include/
│   ├── config.py                 # Gestion centralisée des variables et de la connexion
│   ├── extract.py                # Logique d'extraction des données
│   ├── transform.py              # Logique métier de nettoyage (Data Cleaning)
│   ├── data_quality.py           # Logique des garde-fous qualité (Data Quality)
│   ├── load.py                   # Connexion et chargement SQLAlchemy vers Postgres
│   └── test_pipeline.py          # Script d'intégration pour tester l'ETL de bout en bout
├── tests/
│   └── test_pipeline_sales_dags.py # Tests de validation de la structure du DAG
├── .env                          # Variables d'environnement locales (Sécurisé) 
├── .gitignore                    # Exclusion des fichiers système, secrets et caches
└── Dockerfile                    # Image personnalisée Astro Runtime avec dépendances C

````

## 🔌 Documentation des Étapes ETL

### 1. Étape d'Extraction (`Extract`)
- Fichier : `include/extract.py`
- Composant : `extract_data_callable()`
- Il extrait les données à l'aide d'un chemin d'accès absolu reconstruit dynamiquement (`DATA_PATH`) basé sur la racine du projet, évitant ainsi les ruptures de chemins d'exécution sous Docker.

### 🛠️ 2. Étape de Transformation (`Transform`)
- **Fichier :** `include/transform.py`
- **Composant :** `transform_data_callable(df)`
- **Règles de Gestion Appliquées :** 
    - **Standardisation :** Passage des colonnes en minuscules, remplacement des espaces par des `_` et suppression des espaces aux extrémités (strip).
    - **Intégrité :** Suppression des lignes strictement identiques. Les identifiants absents ou dupliqués restent bloquants au contrôle qualité.
    - **Imputation :** Seuls les champs textuels vides sont remplacés par `'unknown'`. Aucun montant ou pays n'est inventé.
    - **Normalisation textuelle :** Uniformisation des genres (`male/m` $\rightarrow$ `M`) et nettoyage par Regex de la colonne age (ex: `"25 years"` $\rightarrow$ `25`). Les âges aberrants restent visibles et bloquent le chargement. Les dates non interprétables sont également rejetées.

### 🛡️ 3. Étape de Validation Qualité (Data Quality)

- **Fichier :** `include/data_quality.py`
- **Composant :** `data_quality_callable(df)`
- Cette étape agit comme un **pare-feu (Gate)**. Elle utilise le logger officiel d'Airflow (`airflow.task`) et lève des `ValueError`  bloquantes en cas de non-conformité majeure :
    - Absence d'une colonne obligatoire du schéma cible.
    - Présence de valeurs nulles sur les axes critiques (`customer_id`, `purchase_amount`).
    - Détection de montants financiers négatifs ou d'âges hors de la plage normale.

### 💾 4. Étape de Chargement (Load)
- **Fichier :** `include/load.py`
- Composant : `load_data_callable(df)`
- Moteur : `SQLAlchemy` avec le pilote `psycopg2`.
- Une table de staging reçoit le lot validé par paquets de 1 000 lignes. Un `INSERT ... ON CONFLICT (customer_id) DO UPDATE` met à jour `sales_dwh` dans la même transaction. La table cible et les clients absents du lot sont conservés ; un échec annule le chargement et la création du staging.
- **Grain du jeu de données : une ligne d'état courant par client.** `customer_id` est la clé de cet UPSERT. Si la source contient plusieurs ventes par client, il faut un identifiant de vente stable avant d'utiliser ce chargement.
- Sur une ancienne table contenant des `customer_id` dupliqués, la création de l'index unique échoue : réconcilier ces doublons avant de relancer. Aucun doublon n'est supprimé automatiquement.


## 🔒 Configuration & Sécurité

### Gestion des Variables d'Environnement (`.env`)

Les configurations sensibles sont totalement découplées du code et centralisées dans le fichier `.env` (exclu du suivi Git pour des raisons de sécurité évidentes):

```Bash
PostgreSQL_HOST=host.docker.internal  # Permet d'accéder à la machine hôte depuis Docker 
PostgreSQL_PORT=5433 
PostgreSQL_USER=sanoh 
PostgreSQL_PASSWORD=mon_mot_de_passe 
PostgreSQL_DATABASE=sales_dwh 
DATA_PATH=./data/sales_data.csv
```

### Isolation Système (`Dockerfile`)

L'image s'appuie sur `astro-runtime:11.3.0.` Elle bascule temporairement sous l'utilisateur `root` pour compiler et installer de manière sécurisée les bibliothèques système nécessaires au pilote PostgreSQL (compilateur `gcc`, packages de développement `libpq-dev`), avant de restituer les droits d'exécution à l'utilisateur sécurisé non-root `airflow`.  

## 🎛️ Orchestration & Enchaînement (DAG)
Le DAG pipeline_sales est configuré avec `catchup=False` et `max_active_runs=1` pour empêcher le bombardement de la base de données par des exécutions historiques concurrentes.

La transmission des données est assurée via le contexte des tâches d'Airflow (`ti.xcom_pull`) de manière séquentielle :

```Python 
extract_data >> transform_data >> data_quality >> load_data
```

## 🧪 Stratégie de Tests & Validation
Le projet intègre une approche rigoureuse de tests à deux niveaux pour garantir la robustesse avant le déploiement.

### 1. Test d'Intégration ETL (Local / Conteneur)
Le script `include/test_pipeline.py` permet de simuler l'exécution complète des quatre étapes de traitement de manière isolée sans passer par l'ordonnanceur d'Airflow.

### 2. Test Unitaire du DAG (CI/CD Ready)
Le script `tests/test_pipeline_sales_dags.py` utilise la suite `DagBag` d'Airflow pour valider la structure intrinsèque de l'orchestration depuis un dossier isolé :
- Vérification de l'absence totale d'erreurs de syntaxe ou d'importation dans le DAG.
- Validation que le DAG contient précisément les 4 tâches requises.
- Validation stricte des dépendances amont/aval (Upstream/Downstream).

## 🚀 Installation & Lancement Rapide

### Prérequis
- Docker Desktop installé et fonctionnel
- Astro CLI installé sur votre système

### Déploiement local
1. Clonez ce dépôt sur votre machine locale. 
2. Créez votre fichier `.env` à la racine à partir de vos identifiants PostgreSQL.
3. Démarrez l'environnement conteneurisé Astro CLI :

``` Bash 
astro dev start
```
4. Accédez à l'interface Web d'Airflow sur `http://localhost:8080` (Identifiants : `admin` / `admin`).

### Exécution des tests à l'intérieur du conteneur

Pour valider le fonctionnement de votre code dans l'environnement Astro, exécutez le script d'intégration directement dans le conteneur du Scheduler :

``` Bash 
# 1. Entrer dans le conteneur
astro dev bash --scheduler

# 2. Lancer le script de test
python -m include.test_pipeline

```

## Tests

```bash
python -m pytest tests/unit tests/integration -q
# TEST_POSTGRES_URL active les tests PostgreSQL (base dédiée aux tests).
# Dans Astro, les tests du DAG utilisent aussi Airflow :
python -m pytest tests/dags -q
```

Les tests couvrent le rejet des anomalies, les fichiers Parquet, le rejeu sans doublons,
la conservation des clients existants et le rollback après un échec d'insertion.
