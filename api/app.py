# api/app.py

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Configurações e variáveis para cache e categorias
base_url = 'https://wix.maxcine.top/public/filmes'
generos = {
    12: "Aventura", 14: "Fantasia", 16: "Animação", 18: "Drama", 27: "Terror",
    28: "Ação", 35: "Comédia", 36: "História", 37: "Faroeste", 53: "Thriller",
    80: "Crime", 99: "Documentário", 878: "Ficção científica", 9648: "Mistério",
    10402: "Música", 10749: "Romance", 10751: "Família", 10752: "Guerra", 10770: "Cinema TV"
}

cache_filmes = {}
ultima_atualizacao = 0
intervalo_atualizacao = 7 * 24 * 60 * 60  # 7 dias em segundos

def extrair_links(genero_id):
    filmes_links = set()
    page = 1

    while True:
        url = f'{base_url}?genre={genero_id}&page={page}'
        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        series_list = soup.find_all('div', class_='series-list')
        if not series_list:
            break

        for series in series_list:
            links = series.find_all('a')
            for link in links:
                filme_link = link.get('href')
                if filme_link:
                    filmes_links.add(filme_link)

        next_page = soup.select_one('.pagination a:-soup-contains("Próxima")')
        if next_page and 'href' in next_page.attrs:
            page += 1
        else:
            break

    return filmes_links

def extrair_informacoes_filme(url_filme):
    response = requests.get(url_filme)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    titulo = soup.select_one('.titulo h1').text.strip() if soup.select_one('.titulo h1') else None
    capa = soup.select_one('.poster-m img')['src'] if soup.select_one('.poster-m img') else None
    banner = soup.select_one('.backdrop')['style'] if soup.select_one('.backdrop') else None
    ano = soup.select_one('.informacoes li strong').text.strip() if soup.select_one('.informacoes li strong') else None
    sinopse = soup.select_one('.sinopse p').text.strip() if soup.select_one('.sinopse p') else None
    generos_filme = [gen.text.strip() for gen in soup.select('.genero span')]
    
    return {
        "titulo": titulo,
        "capa": capa,
        "banner": banner,
        "ano": ano,
        "sinopse": sinopse,
        "generos": generos_filme
    }

def atualizar_cache():
    global cache_filmes, ultima_atualizacao
    cache_filmes = {}

    for genero_id, genero_nome in generos.items():
        links_filmes = extrair_links(genero_id)
        filmes = []
        
        for link in links_filmes:
            filme_info = extrair_informacoes_filme(link)
            if filme_info:
                filmes.append(filme_info)

        cache_filmes[genero_nome] = filmes

    ultima_atualizacao = time.time()
    print("Cache atualizado com sucesso.")

@app.route('/filmes', methods=['GET'])
def filmes():
    global ultima_atualizacao
    if time.time() - ultima_atualizacao > intervalo_atualizacao:
        atualizar_cache()

    return jsonify(cache_filmes)

atualizar_cache()
