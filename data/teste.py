import pandas as pd

# Caminho para o arquivo CSV
file_path = 'data\links.csv'

# Leitura do arquivo CSV
df = pd.read_csv(file_path)

# Exibindo as primeiras linhas do DataFrame
print(df.head())
# Selecionando apenas a coluna de links
links = df.iloc[:, 1]

# Salvando os links em um arquivo de texto
links_file_path = 'data/links.txt'
links.to_csv(links_file_path, index=False, header=False)

print(f'Links salvos em {links_file_path}')