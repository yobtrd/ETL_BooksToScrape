## On importe les packages dont on aura besoin pour le projet 
# Request pour extraire la page web, BS pour parser les données, et CSV pour les enregistrer)
# On utilisera également la fonction urljoin pour modifier les urls relative et re pour utiliser les regex

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re

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
    url_img = urljoin("https://books.toscrape.com/", url_img_relative)
   
    ## On incorpore la fonction permettant de télécharger l'image
    # On récupère le nom de l'image, les données en bytes et on les enregistre dans un format .jpg écrit en bytes
    reponse = requests.get(url_img)
    img_data = reponse.content
    nom_image = balise_img["alt"]
    with open(f"{nom_image}.jpg", "wb") as fichier:
        fichier.write(img_data)
    
    ## On organise tout ça dans un dico en prévision du chargement et en respectant les exigences
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


## On crée la fonction pour extraire tous les liens des produits d'une page de catégorie
def extract_category(url_category):
    # On scrape la page de catégorie
    reponse = requests.get(url_category)
    page = reponse.content
    soup = BeautifulSoup(page, "html.parser")
    # On crée une liste pour incorporer tous les liens, on y ajoute tous les liens parser grâce à une boucle
    liste_url = []
    h3 = soup.find_all("h3")
    for element in h3:
        lien_brut = element.find_all("a")
        for element in lien_brut:
            href = element["href"]
            href = href.strip("../../")
            page_url = f"https://books.toscrape.com/{href}"
            liste_url.append(page_url)
    return liste_url



## Pour vérifier les instructuctions :
# Exemple de lien :
url_page = "https://books.toscrape.com/catalogue/the-mysterious-affair-at-styles-hercule-poirot-1_452/index.html"
url_category = "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html"

# Pour vérifier extraction page et image:
print(extract(url_page))

# Pour vérifier l'extraction des liens de la page categorie:
print(extract_category(url_category))
# Pour vérifier que le nombre de lien correspond à celui annoncé par catégorie:
print(len(extract_category(url_category)))
