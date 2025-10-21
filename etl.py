## On importe les packages dont on aura besoin pour le projet 
# Request pour extraire la page web, BS pour parser les données, et CSV pour les enregistrer)
# On utilisera également la fonction urljoin pour modifier les urls relative et re pour utiliser les regex

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re
import os


## On crée une fonction pour scraper la page d'un produit avec request et les parser avec BS
def extract(url_page):
    # D'abord le scrap
    reponse = requests.get(url_page)
    page = reponse.content
    # Puis le parse
    soup = BeautifulSoup(page, "html.parser")
    ## On extrait les infos qui nous intéresse, puis on les organise en dico pour pouvoir plus facilement les traiter ensuite
    # Le titre
    titre = soup.find("h1").string
    # Le bloc description, où on récupère que le nombre pour le stock
    info_description = soup.find_all("td")
    upc = info_description[0].get_text()
    prixtaxe = info_description[2].get_text()
    prixstaxe = info_description[3].get_text()
    stock = info_description[5].get_text()
    stock = re.findall("[0-9]+", stock)[0]
    # Description + categorie
    description = soup.find_all("p")[3].get_text()
    categorie = soup.find_all("a")[3].get_text()
    # La note
    note = soup.find_all("p")[2]
    note = note["class"]
    note = note[1]
    # Le lien de l'image complet
    balise_img = soup.find_all("img")[0]
    url_img_relative = balise_img["src"]
    url_img = urljoin(url_page, url_img_relative)
    ## On enregistre les info dans un dico en prévision du chargement et en respectant les exigences
    info = {
        "product_page_url": url_page,
        "universal_ product_code (upc)": upc,
        "title": titre,
        "price_including_tax": prixtaxe,
        "price_excluding_tax": prixstaxe,
        "number_available": stock,
        "product_description": description,
        "category": categorie,
        "review_rating": note,
        "image_url": url_img
    }
    return info
 

## On ajoute la fonction pour extraire tous les liens des produits d'une page de catégorie
def extract_category(url_category):
    # On crée une liste pour incorporer tous les liens
    liste_url = []
    # On va créer une boucle afin de pouvoir extraire les liens de plusieurs pages s'il y en a
    while True:
        reponse = requests.get(url_category)
        page = reponse.content
        soup = BeautifulSoup(page, "html.parser")
        # On ajoute dans la liste tous les liens de la page grâce à une boucle
        h3 = soup.find_all("h3")
        for element in h3:
            lien_brut = element.find_all("a")
            for element in lien_brut:
                url_relative = element["href"]
                page_url = urljoin(url_category, url_relative)
                liste_url.append(page_url)
        # On vérifie s'il existe un lien vers une page suivante
        pg_next_brut = soup.select("li.next")
        if pg_next_brut: 
            # Si c'est le cas on récupère le lien de la page suivant dont on récupérera les données via la boucle...
            pg_next = pg_next_brut[-1].find("a")["href"] 
            url_category = urljoin(url_category, pg_next)            
        # ... jusqu'à qu'il n'y ai plus de page
        else:
            break
    return liste_url


## On ajoute la fonction permettant de télécharger les images
def save_image(url_page):
    # On récupère l'url de l'image pour extraire les données en bytes
    url_img = extract(url_page)["image_url"]
    reponse_url = requests.get(url_img)
    img_data = reponse_url.content
    # On récupère le nom de l'image
    reponse_nom = requests.get(url_page).content
    soup = BeautifulSoup(reponse_nom, "html.parser")
    balise_img = soup.find_all("img")[0]
    nom_img_brut = balise_img["alt"]
    # On modifie le nom de l'image pour être bien référencé et pouvoir fonctionner avec les caractères spéciaux
    nom_img = re.sub(r"(\W)", "", nom_img_brut)
    # On vérifie que le nom d'image n'existe pas déjà pour éviter l'écrasement du fait d'éventuel doublon
    test_doublon = f"data/images/{nom_img}.jpg"
    if os.path.exists(test_doublon):
        # Si c'est le cas on enregistre l'image sous un nom légèrement modifié
        with open(f"data/images/{nom_img}(2).jpg", "wb") as fichier:
            fichier.write(img_data)
    else:
        # Si ok on enregistre les données dans un format .jpg écrit en bytes, avec le nom de base
        with open(f"data/images/{nom_img}.jpg", "wb") as fichier:
            fichier.write(img_data)


            


## On ajoute une fonction permettant d'initialiser un fichier CSV par catégorie
def init_save(url_category):
    with open(f"data/cst/{nom_category}.csv", "w", newline="") as fichierCSV:
        # On remet les catégorie du dico qu'on réutilisera grâce à dictwriter
        fieldnames = [
                    "product_page_url", 
                    "universal_ product_code (upc)", 
                    "title",
                    "price_including_tax", 
                    "price_excluding_tax",
                    "number_available",
                    "product_description", 
                    "category", 
                    "review_rating", 
                    "image_url",
                    ]
        writer = csv.DictWriter(fichierCSV, fieldnames=fieldnames)
        writer.writeheader()
  
              
## On ajoute la fonction permettant d'ajouter chaque nouveau dico dans le fichier CSV
def save(info):
    nom_csv = info["category"]
    with open(f"data/cst/{nom_csv}.csv", "a", newline="") as fichierCSV:
        fieldnames = [
                    "product_page_url", 
                    "universal_ product_code (upc)", 
                    "title",
                    "price_including_tax", 
                    "price_excluding_tax",
                    "number_available",
                    "product_description", 
                    "category", 
                    "review_rating", 
                    "image_url",
                    ]
        writer = csv.DictWriter(fichierCSV, fieldnames=fieldnames)
        writer.writerow(info)

url_category = "https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html"
nom_category = "fantasy"

init_save(url_category)
for url_page in extract_category(url_category):
    info = extract(url_page)
    save(info)
    save_image(url_page)