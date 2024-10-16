import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import numpy as np
from loguru import logger
from .utils.rename_to_snake_case import rename_to_snake_case
from .utils.get_dataset_columns import get_dataset_columns_with_types

load_dotenv()

AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTABLE_ACCESS_TOKEN')
BASE_ID = os.getenv('BASE_ID')
AIRTABLE_URL = f'https://api.airtable.com/v0/{BASE_ID}/'
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
        logger.info(f"Searching for table... {table_name}")
        for table in tables:
            if table.get('name') == table_name:
                logger.info(f"Tabela encontrada: {table_name}")
                return table
        return None
    else:
        logger.error(f"Erro ao buscar tabelas: {response.content}")
        return None

def verify_column_exists(table, column_name):
    """
    Function to check if a column exists in a table

    Args:
        - table: dictionary with the table information
        - column_name: name of the column to check
    """
    for field in table.get('fields', []):
        if field.get('name') == column_name:
            return True
    return False

def create_table(columns, table_name, description=""):
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
        logger.success("Tabela criada com sucesso.")
        logger.info(response.json())
    else:
        logger.error(f"Erro ao criar tabela: {response.content}")

def upsert_data_airtable(
        dataset:pd.DataFrame,
        table_name:str,
        fields_to_merge_on:list, 
        batch_size=10
        ):
    """
    Function to send data to Airtable in batches.
    It uses the upsert feature to update existing records.
    It assumes that the dataset has the same columns as the Airtable table.
    The maximum batch size is 10 records.
    The fields_to_merge_on parameter is a list of fields used as the external key for the upsert.

    Args:
        - dataset: pandas DataFrame with the data to send
        - fields_to_merge_on: list of fields used as the external key for the upsert
        - table_name: name of the table in Airtable
        - batch_size: number of records to send in each batch (default is 10, maximum is 10)
    Returns:
        - None
    """
    all_requests = 0
    success_requests = 0
    error_requests = 0

    dataset = dataset.copy()

    dataset = dataset.replace({np.nan: None})

    for column in dataset.select_dtypes(include=['datetime64[ns, UTC]']).columns:
        dataset[column] = dataset[column].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

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

        response = send_upsert_request_to_airtable(payload, table_name)

        if response.status_code == 200:
            success_requests += 1
            logger.info(f"Lote {i // batch_size + 1} enviado com sucesso.")
        else:
            error_requests += 1
            logger.error(f"Erro no lote {i // batch_size + 1}: {response.content}")

        all_requests += 1

    logger.info(f"Total de requisições: {all_requests}, Sucesso: {success_requests}, Erro: {error_requests}")

def send_upsert_request_to_airtable(payload, table_name):
    """
    Function to send an upsert request to Airtable

    Args:
        - payload: dictionary with the data to send
        - table_name: name of the table in Airtable
    """
    response = requests.patch(AIRTABLE_URL + table_name, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    return response

def send_to_airtable_pipeline(dataframe):
    """
    Function to send a dataset to Airtable.
    It checks if the table exists, creates it if it doesn't, and sends the data.
    Args:
        - dataframe: pandas DataFrame with the data to send
    """
    PRIMARY_FIELD = os.getenv('PRIMARY_FIELD')
    FIELDS_TO_MERGE_ON = os.getenv('FIELDS_TO_MERGE_ON').split(',') if os.getenv('FIELDS_TO_MERGE_ON') else None
    TABLE_NAME = os.getenv('TABLE_NAME')

    table = table_exists(TABLE_NAME)

    if not table:
        columns = get_dataset_columns_with_types(dataset=dataframe, primary_field=PRIMARY_FIELD)
        create_table(
            columns=columns,
            table_name=TABLE_NAME)
    else:
        column_hash_exists = verify_column_exists(table, 'column_hash')
    
        if column_hash_exists is False:
            dataframe = dataframe.drop(columns=['column_hash'])

    upsert_data_airtable(
        dataset=dataframe,
        table_name=TABLE_NAME,
        fields_to_merge_on=FIELDS_TO_MERGE_ON)
