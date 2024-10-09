import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import numpy as np
from utils.rename_to_snake_case import rename_to_snake_case
from utils.get_dataset_columns import get_dataset_columns_with_types

load_dotenv()

PRIMARY_FIELD = os.getenv('PRIMARY_FIELD')
FIELDS_TO_MERGE_ON = os.getenv('FIELDS_TO_MERGE_ON').split(',') if os.getenv('FIELDS_TO_MERGE_ON') else None

AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
BASE_ID = os.getenv('BASE_ID')
TABLE_NAME = os.getenv('TABLE_NAME')
AIRTABLE_URL = f'https://api.airtable.com/v0/{BASE_ID}/' + TABLE_NAME
AIRTABLE_META_URL = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'

headers = {
    'Authorization': f'Bearer {AIRTABLE_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def table_exists(table_name):
    """
    Function to check if a table exists in the Airtable base
    """
    response = requests.get(AIRTABLE_META_URL, headers=headers)
    if response.status_code == 200:
        tables = response.json().get('tables', [])
        print(f"Searching for table... {table_name}")
        return any(table.get('name') == table_name for table in tables)
    else:
        print(f"Erro ao buscar tabelas: {response.content}")
        return False

def create_table(columns, table_name=TABLE_NAME, description=""):
    """
    Function to create a table in the Airtable base
    """
    payload = {
        "name": rename_to_snake_case(table_name),
        "description": description,
        "fields": columns
    }

    response = requests.post(AIRTABLE_META_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Tabela criada com sucesso.")
        print(response.json())
    else:
        print(f"Erro ao criar tabela: {response.content}")

def upsert_data_airtable(dataset:pd.DataFrame, fields_to_merge_on:list, batch_size=10):
    """
    Function to send data to Airtable in batches.
    It uses the upsert feature to update existing records.
    It assumes that the dataset has the same columns as the Airtable table.
    The maximum batch size is 10 records.
    The fields_to_merge_on parameter is a list of fields used as the external key for the upsert.

    Args:
        - dataset: pandas DataFrame with the data to send
        - fields_to_merge_on: list of fields used as the external key for the upsert
        - batch_size: number of records to send in each batch (default is 10, maximum is 10)
    Returns:
        - None
    """
    all_requests = 0
    success_requests = 0
    error_requests = 0

    dataset = dataset.copy()

    dataset = dataset.replace({np.nan: None})

    for column in dataset.select_dtypes(include=['datetime64[ns]']).columns:
        dataset[column] = dataset[column].dt.strftime('%Y-%m-%dT%H:%M:%S')

    for i in range(0, len(dataset), batch_size):
        batch = dataset.iloc[i:i+batch_size]

        records = [
            {
                "fields": {column: row[column] for column in dataset.columns}
            }
            for _, row in batch.iterrows()
        ]

        payload = {}

        if fields_to_merge_on:
            fields_to_merge_on = [rename_to_snake_case(field) for field in fields_to_merge_on]
            payload['performUpsert'] = {
                "fieldsToMergeOn": fields_to_merge_on
            }

        payload['records'] = records

        response = send_upsert_request_to_airtable(payload)

        if response.status_code == 200:
            success_requests += 1
            print(f"Lote {i // batch_size + 1} enviado com sucesso.")
        else:
            error_requests += 1
            print(f"Erro no lote {i // batch_size + 1}: {response.content}")

        all_requests += 1

    print(f"Total de requisições: {all_requests}, Sucesso: {success_requests}, Erro: {error_requests}")

def send_upsert_request_to_airtable(payload):
    """
    Function to send an upsert request to Airtable

    Args:
        - payload: dictionary with the data to send
    """
    response = requests.patch(AIRTABLE_URL, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    return response

def send_to_airtable_pipeline(dataframe):
    """
    Function to send a dataset to Airtable.
    It checks if the table exists, creates it if it doesn't, and sends the data.
    Args:
        - dataframe: pandas DataFrame with the data to send
    """
    if not table_exists(TABLE_NAME):
        columns = get_dataset_columns_with_types(dataset=dataframe, primary_field=PRIMARY_FIELD)
        create_table(columns)

    upsert_data_airtable(dataframe, FIELDS_TO_MERGE_ON)
