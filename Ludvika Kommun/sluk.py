#Stefan Sommarsjö 2024
#https://github.com/sestsom
#Sluk laddar ner kallelser och protokoll från Ludvika.se

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import sys

# URL'er
base_urls = {
    #"Ludvika.se": "https://www.ludvika.se", från början var det tänkt att damsuga allt..
    "Kommunfullmäktige": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kommunfullmaktige/kommunfullmaktige-kf",
    "Kommunstyrelsen": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kommunstyrelsen/kommunstyrelsen-ks",
    "Kommunstyrelsens Finansutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kommunstyrelsen/kommunstyrelsens-arbetsutskott-ks-au",
    "Social och Utbildningsnämnden": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/social--och-utbildningsnamnden/social--och-utbildningsnamnden-sun?folder=19.77fd3e1f18c8ab51ef64a7ec&sv.url=12.9ffae2e16cc22b3e929b88",
    "Kommunstyrelsens Arbetsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kommunstyrelsen/kommunstyrelsens-arbetsutskott-ks-au",
    "Kultur och-samhallsutvecklingsnamndens-arbetsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kultur--och-samhallsutvecklingsnamnden/kultur--och-samhallsutvecklingsnamndens-arbetsutskott-ksu-au",
    "Vård och omsorgsnämnden": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/vard--och-omsorgsnamnden/vard--och-omsorgsnamnden-von",
    "Vård och omsorgsnämndens arbetsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/vard--och-omsorgsnamnden/vard--och-omsorgsnamndens-arbetsutskott--von-au",
    "Kultur och fritidsnämnden": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kultur--och-fritidsnamnden/kultur--och-fritidsnamnden-kfn",
    "Kultur och fritidsnämndens arbetsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kultur--och-fritidsnamnden/kultur--och-fritidsnamndens-arbetsutskott-kfn-au",
    "Kultur och fritidsnämndens bidragsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/kultur--och-fritidsnamnden/kultur--och-fritidsnamndens-bidragsutskott-kfn-bi",
    "Samhällsbyggnadsnämnden": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/samhallsbyggnadsnamnden/samhallsbyggnadsnamnden-sbn",
    "Samhällsbyggnadsnämndens arbetsutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/samhallsbyggnadsnamnden/samhallsbyggnadsnamndens-arbetsutskott-sbn-au",
    "Samhällsbyggnadsnämndens trafik- och lokalutskott": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/samhallsbyggnadsnamnden/samhallsbyggnadsnamndens-trafik--och-lokalutskott-sbn-tlu",
    "Gemensam nämnd för upphandling": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/gemensam-namnd-for-upphandling-gnu",
    "Tillgänglighetsrådet": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/tillganglighetsradet-ktr",
    "Krisledningsnämnden": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/krisledningsnamnden/krisledningsnamnden-kn",
    "Ludvika kommun stadshus AB": "https://www.ludvika.se/kommun-och-politik/politik-och-demokrati/moten-och-protokoll/ludvika-kommun-stadshus-ab-lksab",
}

# Intressant filformat
file_types = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]

# Ladda ner filerna
def download_file(url, folder_name):
    download_folder = os.path.join("filer", folder_name)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Unquote ¤#!%
    local_filename = os.path.join(download_folder, unquote(os.path.basename(urlparse(url).path)))
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Nedladdad: {local_filename}")
    except Exception as e:
        print(f"Misslyckades med att ladda ner {url}: {e}")

# Länkar
def get_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return [urljoin(url, link.get("href")) for link in soup.find_all("a", href=True)]
    except Exception as e:
        print(f"Misslyckades med att hämta länkar från {url}: {e}")
        return []

# Sök igenom rekursivt
def crawl_website(base_url, folder_name, visited=set()):
    try:
        if base_url in visited:
            return
        visited.add(base_url)

        print(f"URL: {base_url}")

        links = get_links(base_url)
        for link in links:
            # Ladda ner filformaten där uppe
            if any(link.endswith(file_type) for file_type in file_types):
                print(f"Hittade fil: {link}")
                download_file(link, folder_name)
            # Leta vidare
            elif base_url in link:
                crawl_website(link, folder_name, visited)
    except KeyboardInterrupt:
        print("\nProcessen avbruten.")
        sys.exit(0)

# Start
for folder_name, base_url in base_urls.items():
    print(f"\nLetar igenom: {folder_name} - {base_url}")
    crawl_website(base_url, folder_name)