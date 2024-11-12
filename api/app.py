from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# URL base da página que contém a lista de filmes
base_url = 'https://wix.maxcine.top/public/filmes'

# Gêneros disponíveis
generos = {
    12: "Aventura",
    14: "Fantasia",
    16: "Animação",
    18: "Drama",
    27: "Terror",
    28: "Ação",
    35: "Comédia",
    36: "História",
    37: "Faroeste",
    53: "Thriller",
    80: "Crime",
    99: "Documentário",
    878: "Ficção científica",
    9648: "Mistério",
    10402: "Música",
    10749: "Romance",
    10751: "Família",
    10752: "Guerra",
    10770: "Cinema TV"
}

# Função para extrair links de filmes de uma categoria
def extrair_links(genero_selecionado):
    filmes_links = set()  # Usar um conjunto para evitar duplicações
    page = 1

    while True:
        url = f'{base_url}?genre={genero_selecionado}&page={page}'

        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            series_list = soup.find_all('div', class_='series-list')

            if not series_list:
                break

            for series in series_list:
                links = series.find_all('a')  # Ajuste conforme a estrutura do HTML
                for link in links:
                    filme_link = link.get('href')
                    if filme_link:
                        filmes_links.add(filme_link)  # Adiciona o link ao conjunto (evitando duplicatas)

            next_page = soup.select_one('.pagination a:-soup-contains("Próxima")')
            if next_page and 'href' in next_page.attrs:
                page += 1
            else:
                break
        else:
            break

    return filmes_links

# Rota para retornar os links de filmes
@app.route('/api/filmes', methods=['GET'])
def get_filmes_links():
    todos_os_links = []
    
    # Extração dos links de filmes para todas as categorias
    for genero_selecionado in generos.keys():
        filmes_links = extrair_links(genero_selecionado)
        todos_os_links.extend(filmes_links)  # Adiciona todos os links extraídos

    return jsonify(list(todos_os_links))

if __name__ == "__main__":
    app.run(debug=True)
