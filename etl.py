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
    # On modifie le nom de l'image pour être bien référencé et pouvoir fonctionner avec les caractères spéciaux
    nom_image = balise_img["alt"]
    nom_image = nom_image.replace(" ", "")
    nom_image = nom_image.replace(":", "") + ".jpg" # /!\ A voir si c'est pas trop long pour certains.
    with open(nom_image, "wb") as fichier:
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
                page_url = urljoin("https://books.toscrape.com/catalogue/.../.../.../", url_relative) # /!\ Pas top mais pas trouvé mieux
                liste_url.append(page_url)
        # On vérifie s'il existe un lien vers une page suivante
        pg_next_verif = len(soup.select("li.next"))
        if pg_next_verif > 0:
            # Si c'est le cas on récupère le lien de la page suivant dont on récupérera les données via la boucle...
            pg_next_brut = soup.select("li.next")[-1]
            pg_next = pg_next_brut.find_all("a")[-1] # /!\ pourquoi chercher href avant fonctionne pas variable["x"] est traité comme une liste ? indexation sur une balise ?
            pg_next = pg_next["href"]
            pg_next_url = urljoin(url_category, pg_next)
            url_category = pg_next_url
        # ... jusqu'à qu'il n'y ai plus de page
        else:
            break
    return liste_url


url_category = "https://books.toscrape.com/catalogue/category/books/religion_12/index.html"

extract_category(url_category)
for elements in extract_category(url_category):
    url_page = elements
    print(extract(url_page))
    
