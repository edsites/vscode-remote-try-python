from flask import Flask, request, render_template
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# Criação do banco de dados e tabela se não existir
def criar_banco():
    conn = sqlite3.connect('dados_web.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Rota inicial: renderiza a página com o formulário de busca
@app.route('/')
def index():
    return render_template('index.html', query=None, resultados=None)

# Rota para buscar dados já armazenados no banco de dados
@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    query = request.args.get('query')  # Termo buscado pelo usuário
    if not query:
        return render_template('index.html', query=None, resultados=None)

    # Conexão com o banco e busca pelo termo
    conn = sqlite3.connect('dados_web.db')
    cursor = conn.cursor()
    cursor.execute('SELECT titulo, url FROM resultados WHERE titulo LIKE ?', ('%' + query + '%',))
    resultados = [{"titulo": row[0], "url": row[1]} for row in cursor.fetchall()]
    conn.close()

    # Exibir resultados encontrados ou mensagem de nenhum resultado
    return render_template('index.html', query=query, resultados=resultados)

# Rota para adicionar novos sites manualmente
@app.route('/adicionar', methods=['POST'])
def adicionar():
    titulo = request.form.get('titulo')
    url = request.form.get('url')

    if titulo and url:
        conn = sqlite3.connect('dados_web.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO resultados (titulo, url) VALUES (?, ?)', (titulo, url))
        conn.commit()
        conn.close()
        return render_template('index.html', query=None, resultados=None, mensagem="Site adicionado com sucesso!")
    else:
        return render_template('index.html', query=None, resultados=None, mensagem="Erro: Campos obrigatórios não preenchidos.")

# Função para executar o crawler e coletar dados da web
def crawler(url, dominio_base=None):
    try:
        print(f"Coletando dados de: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Verifica erros HTTP
        soup = BeautifulSoup(response.text, 'html.parser')

        novos_dados = []
        conn = sqlite3.connect('dados_web.db')
        cursor = conn.cursor()

        for link in soup.find_all('a', href=True):
            titulo = link.get_text(strip=True)
            url_link = urljoin(dominio_base or url, link['href'])

            # Verifica se o link já existe no banco antes de adicionar
            cursor.execute('SELECT COUNT(*) FROM resultados WHERE url = ?', (url_link,))
            if cursor.fetchone()[0] == 0 and titulo and url_link:
                novos_dados.append((titulo, url_link))

        # Insere novos dados no banco
        if novos_dados:
            cursor.executemany('INSERT INTO resultados (titulo, url) VALUES (?, ?)', novos_dados)
            conn.commit()
            print(f"{len(novos_dados)} novos dados adicionados!")
        else:
            print("Nenhum dado válido encontrado.")
        conn.close()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")

# Inicialização do banco de dados ao iniciar o servidor
criar_banco()

if __name__ == '__main__':
    # Coletar dados dos seus sites antes de iniciar o servidor
    crawler("https://biosinergicos.com.br/aglarefuah/", dominio_base="https://biosinergicos.com.br/aglarefuah/")
    crawler("https://biosinergicos.com.br", dominio_base="https://biosinergicos.com.br")

    # Executar o servidor Flask
    app.run(debug=True)