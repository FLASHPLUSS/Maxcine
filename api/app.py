# api/app.py

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# URL base do site
base_url = 'https://wix.maxcine.top/public/filmes'
generos = {
    12: "Aventura", 14: "Fantasia", 16: "Animação", 18: "Drama", 27: "Terror",
    28: "Ação", 35: "Comédia", 36: "História", 37: "Faroeste", 53: "Thriller",
    80: "Crime", 99: "Documentário", 878: "Ficção científica", 9648: "Mistério",
    10402: "Música", 10749: "Romance", 10751: "Família", 10752: "Guerra", 10770: "Cinema TV"
}

# Cache temporário
cache_temporario = {}
ultima_atualizacao = 0
intervalo_cache = 5 * 60  # Cache de 5 minutos

def extrair_links(genero_id):
    """Extrai links de filmes de uma categoria específica em tempo real."""
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

    return list(filmes_links)

@app.route('/api/filmes', methods=['GET'])
def todos_filmes():
    global ultima_atualizacao, cache_temporario

    # Atualiza o cache se o intervalo expirou
    if time.time() - ultima_atualizacao > intervalo_cache:
        cache_temporario = {}
        for genero_id in generos:
            links_filmes = extrair_links(genero_id)
            cache_temporario[generos[genero_id]] = links_filmes
        ultima_atualizacao = time.time()

    return jsonify(cache_temporario)

# Inicializa o cache com dados em tempo real
cache_temporario = {}
for genero_id in generos:
    links_filmes = extrair_links(genero_id)
    cache_temporario[generos[genero_id]] = links_filmes

if __name__ == "__main__":
    app.run(debug=True)
