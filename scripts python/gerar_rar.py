import subprocess
import os

def criar_arquivo_rar(caminho_pasta, arquivo_rar_destino):
    # Verifica se o caminho do WinRAR está correto
    rar_executavel = r"C:\Program Files\WinRAR\rar.exe"  # Ajuste conforme o seu caminho

    # Certifique-se de que a pasta de origem existe
    if os.path.isdir(caminho_pasta):
        # Construa o comando para compactar a pasta
        comando = [rar_executavel, 'a', arquivo_rar_destino, os.path.join(caminho_pasta, '*')]

        try:
            subprocess.run(comando, check=True)
            print(f"Arquivo RAR criado com sucesso em: {arquivo_rar_destino}")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar arquivo RAR: {e}")
    else:
        print(f"A pasta {caminho_pasta} não existe.")

# Exemplo de uso
caminho_pasta = r"./data/postos_solo"
arquivo_rar_destino = r"./data/todos_os_postos.rar"
criar_arquivo_rar(caminho_pasta, arquivo_rar_destino)
