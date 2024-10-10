# etl-from-excel

# Problema

<p align="justify">
O cliente precisa de um pipeline para subir e transformar uma planilha de Excel. Ele deseja que essa planilha seja enviada a partir de uma interface qualquer, e que o pipeline faça a transformação dos dados e os envie para uma tabela de saída. O pipeline deve ser automático, sem a necessidade de intervenção humana.
</p>

# Solução

<p align="justify">
Para resolver o problema, foi criado um pipeline que recebe a planilha a partir de um bot no Discord, faz a transformação dos dados e os envia para uma tabela no Airtable. O pipeline é composto por três partes: a interface de envio, o ETL e a atualização da tabela gravada no Airtable.
</p>

## Interface de envio

<p align="justify">
A interface de envio é um bot no Discord que recebe a planilha de Excel e a envia para o pipeline. O bot foi criado utilizando a biblioteca <code>discord.py</code>. Ele é ativado ao rodar o script <code><a href="etl_from_excel/main.py">main.py</a></code> e lê as mensagens no servidor em que está conectado. Quando uma mensagem contendo um arquivo de Excel é enviada, o bot salva o arquivo temporariamente e envia o caminho do arquivo para o pipeline de ETL.
</p>

## ETL

<p align="justify">
O ETL é responsável por fazer a transformação dos dados da planilha de Excel e enviá-los para a tabela no Airtable. Seu main está no arquivo <code><a href="etl_from_excel/etl.py">etl.py</a></code>. Atualmente, o ETL está usando Pandas e requests para fazer a transformação e enviar os dados para o Airtable, respectivamente. Ele começa lendo o arquivo e renomeando as colunas, para então tratar as colunas que precisam de transformação. Por fim, ele envia os dados para a tabela no Airtable.
</p>

## Atualização da tabela no Airtable

<p align="justify">
A atualização da tabela no Airtable é feita pelo ETL. Primeiro, o ETL script verifica se a tabela existe no Airtable e cria caso não exista. O ETL verifica se a linha já existe na tabela e, caso exista, atualiza os dados. Caso contrário, ele insere uma nova linha na tabela.
</p>

# Como rodar

## Dependências

1. Uma conta no Discord
2. Uma conta no Airtable
3. Python 3.12 e pip instalados
2. Poetry instalado (`pip install poetry`)

## Passos
1. Clone o repositório
2. Instale as dependências com `poetry install`
3. Crie um arquivo `.env` na raiz do projeto de acordo com o exemplo contido em [`.env.example`](.env.example)
4. Rode o script `main.py` com `poetry run python -m etl_from_excel.main`
5. Com o bot rodando, envie uma mensagem com um arquivo de Excel para o bot no Discord

## Como rodar os testes
1. Rode o comando `poetry run pytest` na raiz do projeto

## Como utilizar o bot

1. Adicione o bot ao seu servidor do Discord
2. Envie uma mensagem com um arquivo de Excel anexado e o seguinte corpo sem os comentários:
```bash
# Nome da aba que será lida (pode deixar em branco)
SHEET_NAME=nome_da_aba
# Número da linha onde começa o cabeçalho (onde estão os nomes das colunas)
HEADER_ROW=13
# Nome da(s) coluna(s) que contém a quantidade a ser tratada
QUANTITY_COLUMNS=ColunaQuantidade
# Nome da(s) coluna(s) que contém a data e hora da transação
DATE_COLUMNS=ColunaData/hora
# Nome da coluna que será usada como chave primária
# Caso não exista, ele pegará a primeira coluna do arquivo
PRIMARY_FIELD=ColunaChavePrimária
# Nome da(s) coluna(s) que serão usadas para juntar as informações com as que já estão na tabela
FIELDS_TO_MERGE_ON=ColunaData/hora,ColunaLocal,ColunaProduto
# Nome da(s) coluna(s) que serão selecionadas para serem inseridas na tabela
# Caso não exista, ele pegará todas as colunas do arquivo. Só deixar em branco se quiser todas as colunas
COLUMNS_TO_SELECT=ColunaData/hora,ColunaLocal,ColunaProduto,ColunaQuantidade,ColunaValor
# Colunas que serão usadas para fazer o hash usado para mesclar as informações (equivalente a chave composta de uma tabela)
COLUMNS_TO_HASH=ColunaData/hora,ColunaLocal,ColunaProduto
# Nome da tabela do Airtable que será usada (se não existir, ele criará uma nova)
TABLE_NAME=nome_que_eu_quero_para_minha_nova_tabela_ou_que_já_existe_no_airtable
```

Para testar se o bot está conseguindo ler suas mensagens, envie uma mensagem com o texto `ping` e veja se ele responde com `pong`.