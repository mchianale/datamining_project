import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import callerAPI as  callerAPI
from dotenv import load_dotenv
load_dotenv()
MAX_CRITIQUES = int(os.getenv("MAX_CRITIQUES"))  

columns = [
    'public', 'note_presse', 'nb_notes_presse',
    'nb_critiques_presse', 'note_spectateurs', 'nb_notes_spectateurs',
    'nb_critiques_spectateurs', 'date', 'duree', 'distributeur', 'recompenses',
    'type', 'box_office_france', 'langues', 'couleur', 'nationalite'
]

def convert_month(month):
    map_month = {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12"
    }
    return map_month[month]

# casting page
def get_casting(id):
    url = f"https://www.allocine.fr/film/fichefilm-{id}/casting/"
    response = requests.get(url)
    if response.status_code == 200:
        if response.url != url:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        # realisator
        rea = soup.find("section", class_="casting-director")
        realisators_obj = []
        if rea:
            realisators = rea.find_all("div", class_="meta-title")
            
            for realisator in realisators:
                realisators_obj.append({
                    "id_film" : id,
                    "realisateur" : realisator.text.strip()
                    })
        # actor name and role
        act = soup.find("section", class_="casting-actor")
        actors_obj = []
        if act:
            actors = act.find_all("div", class_="meta-title")
            roles = act.find_all("div", class_="meta-sub")
            
            for i in range(len(actors)):
                try:    
                    role = ' : '.join(roles[i].text.strip().split(" : ")[1:])
                except:
                    role = None
                actors_obj.append({
                    "id_film" : id,
                    "acteur": actors[i].text.strip(),
                    "role": role
                })

        # scenarist
        sc = soup.find("div", class_="casting-list-gql")
        scenarists_obj = []
        if sc:
            scenarists = sc.find_all("span", class_="link-empty")
            for scenarist in scenarists:
                scenarists_obj.append({
                    "id_film" : id,
                    "scenariste" : scenarist.text.strip()
                    })
        return realisators_obj, actors_obj, scenarists_obj
    
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
# get critiques 
def get_critiques(id, page_id, max_critiques=None):
    url = f"https://www.allocine.fr/film/fichefilm-{id}/critiques/spectateurs/?page={page_id}"
    response = requests.get(url)
    if response.status_code == 200:
        if page_id != 1 and response.url != url:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        critiques = []
        critiques_list = soup.find_all("div", class_="review-card")
        if max_critiques:
            critiques_list = critiques_list[:min(max_critiques, len(critiques_list))]
        for critique in critiques_list:
            author = critique.find('div', class_='meta-title').text.strip()
            stars = float(critique.find('span', class_='stareval-note').text.strip().replace(",", "."))
            # Publiée le DD month year
            date = critique.find('span', class_='review-card-meta-date').text.strip()
            date = date.split(' ')[2:]
            date = f"{date[0]}-{convert_month(date[1])}-{date[2]}"
            content = critique.find('div', class_='review-card-content').text.strip()
            stats = critique.find('div', class_='reviews-users-comment-useful').text.strip()
            stats = stats.split()
            likes = int(stats[0])
            dislikes = int(stats[1])
            critiques.append({
                "id_film": id,
                "auteur": author,
                "note": stars,
                "date": date,
                "contenu": content,
                "likes": likes,
                "dislikes": dislikes
            })
        return critiques
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
# movie page    
def get_movie_information(url):
    response = requests.get(url, timeout=(3.05, 27))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        film_id = int(url.split("=")[1].split(".")[0])
        titre = soup.find("div", class_="titlebar-title-xl").text.strip()
        result = {
            "id": film_id,
            "url" : url,
            "titre": titre,       
        }
        for key in columns:
            result[key] = None
          

        # get synopsis
        synopsis = soup.find("p", class_="bo-p")
        # si pas de synopsis le film est inconnu 
        try:
            synopsis = synopsis.text.strip()
        except:
            return None
        result["synopsis"] = synopsis
        # get public
        try:
            public = soup.find("span", class_="certificate-text").text.strip()
        except:
            public = None
        result["public"] = public
        # note 
        notes = soup.find_all("div", class_="rating-item-content")
        for note in notes:
            titre_note = note.find("span", class_="rating-title")
            if titre_note:
                titre_note = titre_note.text.strip()
            else:
                titre_note = note.find("a", class_="rating-title").text.strip()
            if titre_note in ['Presse', 'Spectateurs']:
                result[f"note_{titre_note.lower()}"] = float(note.find("span", class_="stareval-note").text.strip().replace(",", "."))
                
                info_note = note.find("span", class_="stareval-review light").text.strip().split()
                if titre_note in ['Spectateurs']:
                    # nb_notes notes, nb_critiques critiques
                    result[f"nb_notes_{titre_note.lower()}"] = int(info_note[0])
                    if len(info_note) < 3:
                        result[f"nb_critiques_{titre_note.lower()}"] = 0
                    else:
                        result[f"nb_critiques_{titre_note.lower()}"] = int(info_note[2])
                else:
                    result[f"nb_notes_{titre_note.lower()}"] = int(info_note[0])
                    result[f"nb_critiques_{titre_note.lower()}"] = int(result[f"nb_notes_{titre_note.lower()}"])
        # info 
        info = soup.find("div", class_="meta-body-info")
        try:
            date = info.find("span", class_="date").text.strip().split(' ')
            result['date'] = f"{date[0]}-{convert_month(date[1])}-{date[2]}"
        except:
            if "Prochainement" in info.text:
                result['date'] = "prochainement"
            if "inconnue" in info.text:
                result['date'] = "inconnue"
            else:
                result['date'] = None
        categories = info.find_all("span", class_="dark-grey-link")
        categories = [{"id_film" : film_id, "categorie" : c.text.strip()} for c in categories]
        noisy_content = ''.join(info.text.strip().split('|')).split('\n')
        result['duree'] = None
        for content in  noisy_content:
            content = content.strip()
            try:
                split_h = content.split('h')
                result['duree'] = int(split_h[0])*60 + int(''.join(split_h[-1:]).split('min')[0]) # en minute
                break
            except:
                continue
        
        map_content = {
            "Box Office France": "box_office_france",
            "Nationalité": "nationalite",
            "Langues": "langues",
            "Couleur": "couleur",
            "Type de film": "type",
            "Distributeur": "distributeur",
            "Récompenses": "recompenses"
        }
        techniques = soup.find("section", class_="ovw-technical") 
        techniques = techniques.find_all("div", class_="item")
        for technique in techniques:
            all = technique.find_all("span")
           
            key = all[0].text.strip()
            if key in map_content:
                key = map_content[key]
            else:
                continue
            result[key] = all[1].text.strip()
            result[key] = None if result[key] == "-" else result[key]
            if key == "box_office_france":
                result[key] = int(''.join(result[key].split(' entrées')).replace(" ", ""))

        if result['recompenses']:
            # get number of recompenses
            recompenses = result['recompenses'].split(' ')
            result['recompenses'] = int(recompenses[0])
        else:
            result['recompenses'] = 0

        # add le film 
        # get tags
        try:
            div = soup.find_all("ul", class_="mdl-more")[-1]
            tags = div.find_all("li", class_="mdl-more-li")
            new_tags = []
            for i in range(len(tags)):
                t = '('.join(tags[i].text.split('(')[:-1]).strip()
                new_tags.append({"id_film" : film_id, "tag" : t})
               
                
        except:
            new_tags = []
        #result['tags'] = new_tags
         

        res = get_casting(film_id)
        if res:
            realisators, actors, scenaristes = res
        else:
            div = soup.find("div", class_="meta-body")
            # get actors
            div_actors = div.find("div", class_="meta-body-actor")
            if div_actors:
                actors = div_actors.find_all("span", class_="dark-grey-link")
                actors = [{"id_film" : film_id, "acteur" : actor.text.strip(), "role" : None} for actor in actors]
            else:
                actors = []
            div  = soup.find_all("div", class_="meta-body-direction")

            # get realisators 
            if len(div) >= 1: 
                div_realisators = div[0]
                if div_realisators:
                    realisators = div_realisators.find_all("span", class_="dark-grey-link")
                    realisators = [{"id_film" : film_id, "realisateur" : realisator.text.strip()} for realisator in realisators]
                else:
                    realisators = []
            else:
                realisators = []

            # get scenaristes
            if len(div) >= 2:
                div_scenaristes = div[1]
                if div_scenaristes:
                    scenaristes = div_scenaristes.find_all("span", class_="dark-grey-link")
                    scenaristes = [{"id_film" : film_id, "scenariste" : scenariste.text.strip()} for scenariste in scenaristes]
                else:
                    scenaristes = []
            else:
                scenaristes = []
        
      
       
            
        #result['realisateurs'] = realisators
        #result['acteurs'] = actors
        #result['scenaristes'] = scenaristes
         
        # get critiques
        critiques = []
        page_id = 1
        while True:
            critiques_page = get_critiques(film_id, page_id, max_critiques=MAX_CRITIQUES-len(critiques))
            if critiques_page:
                critiques += critiques_page
                page_id += 1
            else:
                break
            if len(critiques) >= MAX_CRITIQUES:
                break
        #result['critiques'] = critiques
        # date of scrapping
        #result['date_scrapping'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
       
        return result, actors, realisators, scenaristes, critiques, categories, new_tags
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

 
def add_to_db(url):
    res = get_movie_information(url)
    if not res:
        return 
    result, actors, realisators, scenaristes, critiques, categories, new_tags = res
     
    res = callerAPI.insert(table_name="films", data=result)
    if not res:
        return 
    for acteur in actors:
        callerAPI.insert("acteurs", acteur)
    for realisateur in realisators:
        callerAPI.insert("realisateurs", realisateur)      
    for scenariste in scenaristes:
        callerAPI.insert("scenaristes",scenariste)
    for categorie in categories:
        callerAPI.insert("categories", categorie)
    for tag in new_tags:
        callerAPI.insert("tags", tag)
    for critique in critiques:
        callerAPI.insert("critiques", critique)

