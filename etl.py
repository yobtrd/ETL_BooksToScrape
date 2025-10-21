## On importe les packages dont on aura besoin pour le projet (resquest pour extraire la page web, Pillow pour exraire les images, BS pour parser les données, et CSV pour les enregistrer)
import requests
from bs4 import BeautifulSoup
import csv

## On crée une fonction pour scraper la page d'un produit avec request et les parser avec BS
# D'abord le scrap
def extract(url_page):
    reponse = requests.get(url_page)
    page = reponse.content

    # Puis le parse
    soup = BeautifulSoup(page, "html.parser")

    ## On récupère les premières infos du bloc "description", en les organisant en dico pour pouvoir plus facilement les extraire ensuite
    # On crée une liste qui a pour but de concentrer toutes les infos
    infos = []
   
    # Le tritre
    titre = soup.find("h1").string

    # Le bloc description (mettre une boucle ?)
    info1 = soup.find_all("td")
    upc = info1[0].get_text()
    prixtaxe = info1[2].get_text()
    prixstaxe = info1[3].get_text()
    stock = info1[5].get_text()

    # Description + categorie
    description = soup.find_all("p")[-1].get_text()
    categorie = soup.find_all("a")[-1].get_text()

    #La note
    bloc_note = soup.find_all("p")[2]
    note_brut = bloc_note["class"]
    note = note_brut[1]

    # Lie lien de l'image complet
    img_brut = soup.find_all("img")[0]
    img = img_brut["src"]
    url_brut = img.strip("../../")
    url_img = f"https://books.toscrape.com/{url_brut}"
    

    # On organise tout ça dans un dico en prévision de l'extraction et en respectant les exigences
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
    infos.append(info)
    
    return infos



## On crée la fonction pour enregistrer l'image d'une page
def extract_img(page_to_extract):
    for element in page_to_extract:
        url_img = element["image_url"]
    reponse = requests.get(url_img)
    img_data = reponse.content
    with open("fichiertest.jpg", "wb") as fichier:
        fichier.write(img_data)




# Pour vérifier extraction page :
url_page = "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html"

extract(url_page)
print(extract(url_page))

# Pour vérifier extraction image :
page_to_extract = extract(url_page)
extract_img(page_to_extract)

#