"""
Moduł zawiera funkcje wczytujące i przetwarzajace dane ze strony wydziału
"""

import os
import time
import json
import collections
import requests
from lxml import html


def load_data(path):
    """Wczytuje dane z pliku zawierającego dane o autorach i publikacjach"""

    with open(path, 'r') as file:
        apacz = json.load(file)

    units = []
    for _, value in apacz['authors'].items():
        units.extend(value['units'])

    return apacz, set(units)


def download_publications(url, save_dir):
    """Pobiera i zapisuje publikacje"""

    # pobranie lat dla których są dostępne publikacje
    url_wmii = url
    url_papers = url_wmii + '/jednostki/1-wydzial-matematyki-i-informatyki-uj'

    page = requests.get(url_papers)
    tree = html.fromstring(page.content)

    years = tree.xpath('/html/body/div/div[3]/div[1]/div[2]/a/text()')

    # pobranie publikacji
    os.makedirs(os.path.dirname(os.path.join(save_dir, 'wmii_pages', 'papers', '')), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.join(save_dir, 'wmii_pages', 'authors', '')), exist_ok=True)

    for year in years:
        print(year + '...')
        url_year = url_papers + '?rok=' + year
        time.sleep(0.2)
        page = requests.get(url_year)
        with open(os.path.join(save_dir, 'wmii_pages', 'papers', 'year_') + year, 'bw') as file:
            file.write(page.content)


def download_authors_info(authors_info, save_dir):
    """Pobiera i zapisuje dodatkowe dane o autorach"""

    for i, author in enumerate(authors_info):
        print(f'({i+1}/{len(authors_info)}) {author}...')
        time.sleep(0.2)
        url_auth = authors_info[author]["url"]
        page = requests.get(url_auth)
        with open(os.path.join(save_dir, 'wmii_pages', 'authors', author), 'bw') as file:
            file.write(page.content)

def parse_apacz(data_dir, json_filename='apacz.json', cache=True,
                url_wmii='https://apacz.matinf.uj.edu.pl'):
    """Parsuje stronę z publikacjami po uprzednim ich pobraniu."""

    if not cache:
        download_publications(url=url_wmii, save_dir=data_dir)

    # utworznie słownika z danymi o autorach
    authors_info = {}

    years_dir = os.path.join(data_dir, 'wmii_pages', 'papers')

    for year in os.listdir(years_dir):
        with open(os.path.join(years_dir, year), 'br') as file:
            page_content = file.read()

        tree = html.fromstring(page_content)
        publications = tree.xpath('/html/body/div[@id="page"]/div[@id="content"]/div[@id="yw0"]' \
                   '/div[@class="items"]/div[@class="row-fluid"]')

        for publication in publications:
            authors = [str(x) for x in publication.xpath('div/div[1]/a/text()')]
            authors_urls = [str(x) for x in publication.xpath('div/div[1]/a/@href')]

            title = publication.xpath('div/div[2]/a[1]/text()')[0]
            for author, author_url in zip(authors, authors_urls):
                if author not in authors_info:
                    first_name, *last_names = author.split()
                    authors_info[author] = {"first_name": first_name,
                                            "last_name": ' '.join(last_names),
                                            "url": url_wmii + author_url,
                                            "papers": [title]}
                else:
                    authors_info[author]["papers"].append(title)

    if not cache:
        download_authors_info(authors_info, save_dir=data_dir)

    # uzupełnienie danych w słowniku
    for author in authors_info:
    #     print(author)
        with open(os.path.join(data_dir, 'wmii_pages', 'authors', author), 'br') as file:
            page_content = file.read()
        tree = html.fromstring(page_content)
        auth_units = tree.xpath('/html/body/div/div[3]/div[1]/div[2]/ul/li/text()')

        authors_info[author]["units"] = auth_units

    # utworznie drugiego słownika
    papers_info = collections.defaultdict(list)

    for author, value in authors_info.items():
        for paper in value['papers']:
            papers_info[paper].append(author)


    # zapisz dane
    with open(os.path.join(data_dir, json_filename), 'w') as file:
        json.dump({'authors': authors_info, 'papers': papers_info}, file)
