import asyncio
from bs4 import BeautifulSoup
import requests


async def get_Films(name):
    try:
        web = 'www.kinopoisk.cx'
        url = f'https://www.kinopoisk.ru/index.php?kp_query={name}'
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "lxml")
        a = soup.find('p', class_='name')
        b = soup.find('span', class_='year')
        results = soup.find_all('div', class_='element')
        if a is None or b is None:
            return None
        clear_b = "".join(b.text.strip())
        rt = a.find('a')['href'][:-6]
        if a.find('a').text[-7:-1] == 'фильм':
            rt = rt.replace('film', 'series')
        url_it = web + rt
        name_film = a
        return url_it, clear_b, results, name_film
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


async def get_Rec():
    web = 'www.kinopoisk.cx'
    search = 'Форсаж'
    url = f'https://www.kinopoisk.ru/index.php?kp_query={search}'
    title = []
    link = []
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')

    top_250_block = soup.find('dl', class_='block block_top250')

    if top_250_block:
        movie_entries = top_250_block.find_all('dd', class_='dl')

        for entry in movie_entries:
            movie_link = entry.find('a')
            try:
                russian_title = movie_link.find('s').text.strip()
            except AttributeError:
                russian_title = movie_link.text.strip()
            try:
                movie_url = movie_link['href']
            except KeyError:
                movie_url = "URL не найден"
            title.append(russian_title)
            link.append(web+movie_url)
        return title, link



