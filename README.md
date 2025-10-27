# ETL Books to Scrape

## Description
Version bêta d'un pipeline ETL visant à surveiller les prix de sites concurrents concernant des livres d'occasions. Ici limitée à un site (books.toscrape.com) et via une extraction à la demande et non en temps réel. 

## Installation
- Python doit être préalablement installé.
- Cloner le repository à l'emplacement de votre choix.
- Déplacez-vous dans le dossier du repository (ETL_BooksToScrape) via un terminal, l'ensemble des prochaines étapes se feront via le terminal et dans ce répertoire de travail.
- Créer votre environnement virtuel avec la commande `python -m venv env`.
- Activer l'environnement virtuel avec la commande `env/scripts/activate` sous windows, `source env/bin/activate` sous mac (dans le cas où vous aurez des soucis avec windows, regardez pour changer les stratégies d’exécution de PowerShell).
- Installer les packages et modules nécessaire avec `pip install -r requirements.txt`.

## Usage
- Toujours via le terminal, lancer le script via `python etl.py`.
- Les données du site se téléchargeront dans un nouveau dossier "data".
