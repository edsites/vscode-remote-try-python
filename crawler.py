import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin

# Função para criar o banco de dados e tabela
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
    print("Banco de dados criado/verificado com sucesso!")

# Função para verificar se a URL já existe no banco de dados
def verificar_url_existe(cursor, url_link):
    cursor.execute('SELECT COUNT(*) FROM resultados WHERE url = ?', (url_link,))
    return cursor.fetchone()[0] > 0

# Função para inserir múltiplos dados no banco
def inserir_dados(novos_dados):
    conn = sqlite3.connect('dados_web.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO resultados (titulo, url) VALUES (?, ?)', novos_dados)
    conn.commit()
    conn.close()
    print(f"{len(novos_dados)} novos dados inseridos com sucesso!")

# Função para coletar dados da web e armazenar no banco
def crawler(url, dominio_base=None):
    try:
        print(f"Coletando dados de: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Lança exceção se houver erro HTTP
        soup = BeautifulSoup(response.text, 'html.parser')

        novos_dados = []
        conn = sqlite3.connect('dados_web.db')
        cursor = conn.cursor()

        for link in soup.find_all('a', href=True):
            titulo = link.get_text(strip=True)
            url_link = link['href']

            # Normaliza URLs relativas para completas
            if dominio_base:
                url_link = urljoin(dominio_base, url_link)

            # Adiciona ao banco somente URLs válidas e não duplicadas
            if titulo and url_link and not verificar_url_existe(cursor, url_link):
                novos_dados.append((titulo, url_link))

        conn.close()

        if novos_dados:
            inserir_dados(novos_dados)
        else:
            print("Nenhum dado válido encontrado na página.")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")

# Configuração inicial e execução do crawler
if __name__ == "__main__":
    # Criar/verificar banco de dados e tabela
    criar_banco()
    
    # Executar o crawler para coletar dados de múltiplos sites
    crawler("https://www.python.org", dominio_base="https://www.python.org")
    crawler("https://flask.palletsprojects.com", dominio_base="https://flask.palletsprojects.com")
    crawler("https://lilith.uno/", dominio_base="https://lilith.uno")