import requests
from bs4 import BeautifulSoup
import sqlite3

# Função para criar o banco de dados e a tabela
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

# Função para coletar dados da web
def crawler(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Conexão com o banco de dados
    conn = sqlite3.connect('dados_web.db')
    cursor = conn.cursor()

    # Extraindo links e seus títulos
    for link in soup.find_all('a', href=True):
        titulo = link.get_text(strip=True)
        url_link = link['href']
        
        # Armazenando no banco de dados
        cursor.execute('INSERT INTO resultados (titulo, url) VALUES (?, ?)', (titulo, url_link))
    
    conn.commit()
    conn.close()
    print("Dados coletados e armazenados com sucesso!")

# Configuração inicial
criar_banco()
crawler("https://exemplo.com")

import sqlite3

# Conectar ao banco de dados (será criado se não existir)
conn = sqlite3.connect('dados_web.db')
cursor = conn.cursor()

# Criar a tabela 'resultados'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS resultados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        url TEXT
    )
''')

# Inserir dados fictícios para teste
cursor.execute('INSERT INTO resultados (titulo, url) VALUES (?, ?)', ('Python Official', 'https://www.python.org'))
cursor.execute('INSERT INTO resultados (titulo, url) VALUES (?, ?)', ('Flask Documentation', 'https://flask.palletsprojects.com'))

conn.commit()
conn.close()

print("Tabela criada e dados inseridos com sucesso!")