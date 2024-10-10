# etl-from-excel

# Problema

O cliente precisa de um pipeline para subir e transformar uma planilha de Excel. Ele deseja que essa planilha seja enviada a partir de uma interface qualquer, e que o pipeline faça a transformação dos dados e os envie para uma tabela de saída. O pipeline deve ser automático, sem a necessidade de intervenção humana.

# Solução

Para resolver o problema, foi criado um pipeline que recebe a planilha a partir de um bot no Discord, faz a transformação dos dados e os envia para uma tabela no Airtable. O pipeline é composto por três partes: a interface de envio, o ETL e a atualização da tabela gravada no Airtable.

## Interface de envio

A interface de envio é um bot no Discord que recebe a planilha de Excel e a envia para o pipeline. O bot foi criado utilizando a biblioteca `discord.py`. Ele é ativado ao rodar o script `main.py` e lê as mensagens no servidor em que está conectado. Quando uma mensagem contendo um arquivo de Excel é enviada, o bot salva o arquivo temporariamente e envia o caminho do arquivo para o pipeline de ETL.

## ETL

O ETL é responsável por fazer a transformação dos dados da planilha de Excel e enviá-los para a tabela no Airtable. Seu main está no arquivo `etl.py`. Atualmente, o ETL está usando Pandas e requests para fazer a transformação e enviar os dados para o Airtable, respectivamente. Ele começa lendo o arquivo e renomeando as colunas, para então tratar as colunas que precisam de transformação. Por fim, ele envia os dados para a tabela no Airtable.

## Atualização da tabela no Airtable

A atualização da tabela no Airtable é feita pelo ETL. Primeiro, o ETL script verifica se a tabela existe no Airtable e cria caso não exista. O ETL verifica se a linha já existe na tabela e, caso exista, atualiza os dados. Caso contrário, ele insere uma nova linha na tabela.

# Como rodar

Para rodar o pipeline, é necessário ter o poetry instalado.

1. Clone o repositório
2. Instale as dependências com `poetry install`
3. Crie um arquivo `.env` na raiz do projeto de acordo com o exemplo contido em [`.env.example`](.env.example)
4. Rode o script `main.py` com `poetry run python main.py`
5. Com o bot rodando, envie uma mensagem com um arquivo de Excel para o bot no Discord
