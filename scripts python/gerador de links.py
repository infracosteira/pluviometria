import os
import csv

# Define o base URL e o diretório contendo os arquivos
base_url = "https://cdn.jsdelivr.net/gh/infracosteira/pluviometria@main/data/postos_solo/"
directory = "./data/postos_solo"

# Obter a lista de arquivos no diretório
files = os.listdir(directory)

# Função para extrair o número inicial do nome do arquivo
def extract_number(filename):
    try:
        return int(filename.split('_')[0])  # Extrai o número antes do "_"
    except ValueError:
        return float('inf')  # Caso não tenha número, ordena por último

# Ordenar os arquivos com base no número extraído
sorted_files = sorted(files, key=extract_number)

# Criar o arquivo CSV e escrever os links
output_file_path = os.path.join('data', 'links.csv')
ignored_files = []

with open(output_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)

    for filename in sorted_files:
        if filename.endswith(".csv"):
            link = base_url + filename
            writer.writerow([link])
        else:
            ignored_files.append(filename)

# Exibir arquivos ignorados para diagnóstico
if ignored_files:
    print("Arquivos ignorados (não são CSV):")
    for ignored_file in ignored_files:
        print(ignored_file)

# Exibir total de links gerados e arquivos no diretório
print(f"Total de arquivos no diretório: {len(files)}")
print(f"Total de links gerados: {len(sorted_files) - len(ignored_files)}")
