from flask import Flask, jsonify, request
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
def extrair_links_em_tempo_real(genero_selecionado):
    url = f'{base_url}?genre={genero_selecionado}'  # URL direta para o gênero selecionado
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        series_list = soup.find_all('div', class_='series-list')  # Encontrando o conteúdo da lista de filmes

        filmes_links = set()  # Usar um conjunto para evitar duplicações

        if not series_list:
            return None  # Retorna None se não encontrar filmes

        # Extrai os links dos filmes
        for series in series_list:
            links = series.find_all('a')  # Ajuste conforme a estrutura do HTML
            for link in links:
                filme_link = link.get('href')
                if filme_link:
                    filmes_links.add(filme_link)  # Adiciona o link ao conjunto (evitando duplicatas)

        return list(filmes_links)  # Retorna os links em formato de lista
    else:
        return None  # Caso a requisição falhe

# Rota para pegar os links de filmes de um gênero
@app.route('/api/filmes', methods=['GET'])
def get_filmes():
    genero = request.args.get('genero', type=int)
    
    if genero not in generos:
        return jsonify({"error": "Gênero inválido"}), 400

    filmes_links = extrair_links_em_tempo_real(genero)
    
    if filmes_links is None:
        return jsonify({"error": "Não foi possível extrair os filmes ou a página não foi encontrada"}), 404

    return jsonify({
        "genero": generos[genero],
        "filmes": filmes_links
    })

if __name__ == '__main__':
    app.run(debug=True)
