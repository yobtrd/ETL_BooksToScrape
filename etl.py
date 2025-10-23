import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re
import os

# Fonction pour extraire tous les liens des catégorie du site
def extract_site(url_site):
    liste_url =[]
    reponse = requests.get(url_site)
    page = reponse.content
    soup = BeautifulSoup(page, "html.parser")
    index = soup.select(".nav-list a")
    for elements in index[1:]: # exclusion du premier lien qui renvoie à l'index
        url_relative = elements["href"]
        url_category = urljoin(url_site, url_relative)
        liste_url.append(url_category)
    return liste_url

# Fonction pour extraire tous les liens des produits d'une page de catégorie
def extract_category(url_category):
    liste_url = []
    # Boucle afin de pouvoir extraire les liens de plusieurs pages s'il y en a
    while True:
        reponse = requests.get(url_category)
        page = reponse.content
        soup = BeautifulSoup(page, "html.parser")
        # Ajout dans la liste tous les liens de la page
        h3 = soup.find_all("h3")
        for element in h3:
            lien_brut = element.find_all("a")
            for element in lien_brut:
                url_relative = element["href"]
                page_url = urljoin(url_category, url_relative)
                liste_url.append(page_url)
        # Vérification de l'existence d'un lien vers une page suivante
        pg_next_brut = soup.select("li.next")
        if pg_next_brut: 
            # Si true, récupératon des liens jusqu'à qu'il n'y ai plus de pages
            pg_next = pg_next_brut[-1].find("a")["href"] 
            url_category = urljoin(url_category, pg_next)            
        else:
            break
    return liste_url

# Fonction pour extraire les données d'un produit et les enregistrer dans un dictionnaire
def extract_page(url_page):
    reponse = requests.get(url_page)
    page = reponse.content
    soup = BeautifulSoup(page, "html.parser")
    # Le titre
    titre = soup.find("h1").string
    # Le bloc description, uniquement le nombre pour le stock
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
    # Enregistrement des infos dans le dico en respectant le cahier des charges
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
 
# Fonction pour initialiser un fichier CSV par catégorie
def init_save(url_category):
    # Récupération du nom de la catégorie pour le mettre comme nom du fichier CSV
    reponse = requests.get(url_category).content
    soup = BeautifulSoup(reponse, "html.parser")
    nom_category = soup.find("h1").string
    # Création du dossier où seront stockés les fichiers CSV
    os.makedirs("data/csv/", exist_ok=True)
    # Création du fichier CSV avec les champs du dictionnaire info
    with open(f"data/csv/{nom_category}.csv", "w", newline="", encoding='UTF-8') as fichierCSV:
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
                
# Fonction pour ajouter chaque données du produit dans le fichier CSV correspondant
def save(info):
    nom_csv = info["category"]
    with open(f"data/csv/{nom_csv}.csv", "a", newline="", encoding='UTF-8') as fichierCSV:
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

# Fonction pour télécharger les images
def save_image(url_page):
    # Récupération des données de l'image
    url_img = extract_page(url_page)["image_url"]
    reponse_url = requests.get(url_img)
    img_data = reponse_url.content
    # Récupération et modification du nom de l'image pour leur référencement
    reponse_nom = requests.get(url_page).content
    soup = BeautifulSoup(reponse_nom, "html.parser")
    balise_img = soup.find_all("img")[0]
    nom_img_brut = balise_img["alt"]
    nom_img_brut = nom_img_brut.split(":")[0]
    nom_img_brut = re.sub(r"(\W)", "", nom_img_brut)
    # Récupération d'une partie de l'id de l'image pour éviter les doublons en cas de noms similaires
    id_img = url_img.split("/")[7]
    id_img = id_img[:7]
    nom_img =  f"{nom_img_brut}.{id_img}"
    # Création du dossier de l'image, où chacune seront stockées suivant leur catégorie
    cat = extract_page(url_page)["category"]
    os.makedirs(f"data/images/{cat}", exist_ok=True)
    # Sauvegarde de l'image
    with open(f"data/images/{cat}/{nom_img}.jpg", "wb") as fichier:
        fichier.write(img_data)
   
# Fonction pour lancer l'ensemble des scripts
def ETL(url_site):
    for url_category in extract_site(url_site):
        init_save(url_category)
        for url_page in extract_category(url_category):
            info = extract_page(url_page)
            save(info)
            save_image(url_page)

# Appel de la fonction pour le site concerné
url_site = "https://books.toscrape.com"
ETL(url_site)
