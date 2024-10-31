import os

caminho_pasta = 'data/postos_solo'
url_base = 'https://github.com/infracosteira/pluviometria/raw/main/data/postos_solo/'
links = []

for nome_arquivo in os.listdir(caminho_pasta):
    if nome_arquivo.endswith('.csv'):
        nome_arquivo_escapado = nome_arquivo.replace(' ', '%20')
        link = url_base + nome_arquivo_escapado
        links.append(f'{nome_arquivo},{link}')

with open('./data/links.csv', 'w') as arquivo:
    for item in links:
        arquivo.write(f'{item}\n')