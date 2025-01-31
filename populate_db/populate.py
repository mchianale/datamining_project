import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os 
import scrapper as scrapper 
from dotenv import load_dotenv
from threading import Thread
import callerAPI as  callerAPI

load_dotenv()

min_annee_id = int(os.getenv("MIN_ANNEE"))
max_annee_id = int(os.getenv("MAX_ANNEE"))
chunck_size = int(os.getenv('CHUNK_SIZE'))

def populate(decennie_id, annee_id, page_id):
    main_url = f"https://www.allocine.fr/films/decennie-{decennie_id}/annee-{annee_id}/?page={page_id}"

    response = requests.get(main_url)
    threads = []
    # Check if the request was successful
    if response.status_code == 200:
        # check if not last page
        if page_id != 1 and response.url != main_url:
            return None
        # get the links of the movies
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        
        list_films = soup.find_all("a", class_="meta-title-link")
        
        for film in list_films:
            url = f"https://www.allocine.fr/{film['href']}"
            thread = Thread(target=scrapper.add_to_db, args=(url,))
            thread.start()
            threads.append(thread)
            if len(threads) >= chunck_size:
                for thread in threads:
                    thread.join()
                threads = []

            links.append({
                "titre": film.text,
                "url": film["href"]
            })
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

    for thread in threads:
        thread.join()
    return links



if __name__ == "__main__":
    # Initialisation de la barre de progression
    pbar = tqdm(desc="Films added", unit=" films")

    for annee_id in range(min_annee_id, max_annee_id):
        decennie_id = annee_id // 10 * 10
        page_id = 1

        while True:
            links = populate(decennie_id, annee_id, page_id)
            
            # Arrêt si aucun lien n'est retourné
            if links is None:
                break
            
            # Mise à jour de la barre pour chaque lien
            pbar.update(len(links))
            
            # Passer à la page suivante
            page_id += 1

    # Fermeture de la barre une fois terminé
    pbar.close()
   
 

