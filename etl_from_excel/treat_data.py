import pandas as pd
from utils.rename_to_snake_case import rename_to_snake_case

def read_data_from_excel(path:str, filename:str, sheet_name:str=None, header:int=0) -> pd.DataFrame:
    """
    Function to read data from an Excel file.
    
    Args:
        - path: path to the file
        - filename: name of the file
        - sheet_name: name of the sheet to read
        - header: row number to use as the header (0-indexed)
    """
    try:
        return pd.read_excel(path + filename, sheet_name=sheet_name, header=header)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
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

def treat_date_column(dataset:pd.DataFrame, column:str) -> pd.DataFrame:
    """
    Function to treat a date column in a dataset.

    Args:
        - dataset: pandas DataFrame with the data to treat
        - column: name of the column to treat
    """
    dataset[column] = pd.to_datetime(
        dataset[column],
        errors='coerce',
        format='%d/%m/%Y %H:%M:%S'
        )
    return dataset

def select_columns(dataset:pd.DataFrame, columns:list) -> pd.DataFrame:
    """
    Function to select columns from a dataset.

    Args:
        - dataset: pandas DataFrame with the data
        - columns: list of columns to select
    """
    new_columns = [rename_to_snake_case(column) for column in columns]
    return dataset[new_columns]

def treat_data_pipeline(
        path, 
        filename, 
        sheet_name, 
        header,
        quantity_column:list=None,
        date_column:list=None,
        columns_to_select:list=None
        ):
    """
    Function to treat the data from an Excel file.
    It reads the data, renames the columns to snake_case, treats the quantity column and the date column.

    Args:
        - path: path to the file
        - filename: name of the file
        - sheet_name: name of the sheet to read
        - header: row number to use as the header (0-indexed)
        - quantity_column: list of names of the columns to treat as quantity (default is None)
        - date_column: list of names of the columns to treat as date (default is None)
    """
    df = read_data_from_excel(
        path=path, 
        filename=filename, 
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
    if columns_to_select:
        df = select_columns(df, columns_to_select)

    return df
