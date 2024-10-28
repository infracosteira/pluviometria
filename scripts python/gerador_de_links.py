import csv
import requests

# URL da pasta no repositório do GitHub
repo_url = 'https://api.github.com/repos/infracosteira/pluviometria/contents/data/postos_solo'

# Faz a requisição para obter o conteúdo da pasta
response = requests.get(repo_url)
if response.status_code == 200:
    # Cria ou limpa o arquivo CSV que irá armazenar os links
    with open('data/links_arquivos.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome do Arquivo', 'Link'])  # Cabeçalho do CSV

        # Itera sobre os arquivos retornados pela API
        for item in response.json():
            # Verifica se o item é um arquivo CSV
            if item['name'].endswith('.csv'):
                nome_arquivo = item['name']
                link_download = f"{item['download_url']}?raw=true"  # Força o download
                
                # Escreve o nome do arquivo e o link no CSV
                writer.writerow([nome_arquivo, link_download])
                print(f'Link do arquivo {nome_arquivo} adicionado ao CSV.')
else:
    print(f'Falha ao acessar o repositório - Código de status: {response.status_code}')
