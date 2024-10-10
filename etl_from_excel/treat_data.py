import pandas as pd
import hashlib
from loguru import logger
from .utils.rename_to_snake_case import rename_to_snake_case

def read_data_from_excel(path:str, sheet_name:str=None, header:int=0) -> pd.DataFrame:
    """
    Function to read data from an Excel file.
    
    Args:
        - path: path to the file
        - sheet_name: name of the sheet to read
        - header: row number to use as the header (0-indexed)
    """
    try:
        return pd.read_excel(path, sheet_name=sheet_name, header=header)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return 0

def rename_columns_to_snake_case(dataset:pd.DataFrame) -> pd.DataFrame:
    """
    Function to rename the columns of a dataset to snake_case.

    Args:
        - dataset: pandas DataFrame with the data to rename the columns
    """
    for column in dataset.columns:
        dataset.rename(columns={column: rename_to_snake_case(column)}, inplace=True)
    return dataset

def treat_quantity_column(dataset:pd.DataFrame, column:str) -> pd.DataFrame:
    """
    Function to treat a quantity column in a dataset.

    Args:
        - dataset: pandas DataFrame with the data to treat
        - column: name of the column to treat
    """
    dataset[column] = dataset[column].apply(lambda x: x.replace('un', '').replace(' ', '') if 'un' in x else x)
    dataset[column] = dataset[column].apply(pd.to_numeric)
    return dataset

def treat_date_column(dataset: pd.DataFrame, column: str, timezone: str = 'America/Sao_Paulo') -> pd.DataFrame:
    """
    Function to treat a date column in a dataset and localize it to a specific timezone.

    Args:
        - dataset: pandas DataFrame with the data to treat
        - column: name of the column to treat
        - timezone: string representing the timezone to localize the dates (default is 'America/Sao_Paulo')
    """
    dataset[column] = pd.to_datetime(
        dataset[column],
        errors='coerce',
        format='%d/%m/%Y %H:%M:%S'
    )

    dataset[column] = dataset[column].dt.tz_localize(timezone)
    dataset[column] = dataset[column].dt.tz_convert('UTC')

    return dataset

def select_columns(dataset:pd.DataFrame, columns:list) -> pd.DataFrame:
    """
    Function to select columns from a dataset.

    Args:
        - dataset: pandas DataFrame with the data
        - columns: list of columns to select
    """
    return dataset[columns]

def generate_row_hash(row: pd.Series) -> str:
    """
    Function to generate a hash from a row in a pandas DataFrame.
    It concatenates the values of the row and generates a hash from the string.

    Args:
        - row: pandas Series with the values of the row
    """
    row_str = ''.join(row.astype(str).values)

    return hashlib.sha256(row_str.encode()).hexdigest()

def add_hash_column(dataset: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Function to add a hash column to the dataset.
    It uses the selected columns to generate the hash.

    Args:
        - dataset: pandas DataFrame with the data
        - columns: list of columns to use to generate the hash
    """
    dataset['column_hash'] = dataset[columns].apply(generate_row_hash, axis=1)
    return dataset

def treat_data_pipeline(
        path, 
        sheet_name, 
        header,
        quantity_column:list=None,
        date_column:list=None,
        columns_to_select:list=None,
        columns_to_hash:list=None
        ):
    """
    Function to treat the data from an Excel file.
    It reads the data, renames the columns to snake_case, treats the quantity column and the date column.

    Args:
        - path: path to the file
        - sheet_name: name of the sheet to read
        - header: row number to use as the header (0-indexed)
        - quantity_column: list of names of the columns to treat as quantity (default is None)
        - date_column: list of names of the columns to treat as date (default is None)
        - columns_to_select: list of names of the columns to select (default is None)
        - columns_to_hash: list of names of the columns to use to generate the hash (default is None)
    """
    df = read_data_from_excel(
        path=path, 
        sheet_name=sheet_name, 
        header=header
    )

    df = rename_columns_to_snake_case(df)

    if quantity_column:
        for column in quantity_column:
            df = treat_quantity_column(df, rename_to_snake_case(column))

    if date_column:
        for column in date_column:
            df = treat_date_column(df, rename_to_snake_case(column))

    if columns_to_hash:
        columns_to_hash = [rename_to_snake_case(column) for column in columns_to_hash]
        df = add_hash_column(df, columns_to_hash)
    
    if columns_to_select:
        columns_to_select = [rename_to_snake_case(column) for column in columns_to_select]
        if columns_to_hash and 'column_hash' not in columns_to_select:
            columns_to_select.append('column_hash')
        df = select_columns(df, columns_to_select)

    return df
