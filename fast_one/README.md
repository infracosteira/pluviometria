Para rodar a aplicação localmente basta dar o comando 'poetry shell' (iniciar o ambiente virtual antes!)

'fastapi dev ./nome_da_pasta/nome_do_arquivo'

foram instaladas algumas bibliotecas auxiliares para ajudar no desenvolvimento do projeto

poetry add --group dev ruff

"padronização da escrita como limite e linhas, se os imports estão em ordem alfabetica, ou se criamos uma variavel com um nome ruim, e até mesmo falar de bibliotecas ou variaveis não usadas"

'ruff check . --fix' para corrigir erros. 

![alt text](image.png)

tambem adicionamos o pytest para realizar testes

poetry  add --group  dev pytest pytest-cov
