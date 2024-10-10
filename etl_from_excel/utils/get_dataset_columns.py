from .rename_to_snake_case import rename_to_snake_case

def get_dataset_columns_with_types(dataset, primary_field=None):
    """
    Function to get the columns of a dataset with their types.
    If a primary_field is provided, it will be the first column in the list.

    Args:
        - dataset: pandas DataFrame with the data
        - primary_field: name of the primary field (default is None)
    
    Returns:
        - columns: list of dictionaries with the name, type and options of each
    """
    columns = []

    if primary_field and primary_field in dataset.columns:
        dataset = dataset[[primary_field] + [col for col in dataset.columns if col != primary_field]]

    for column in dataset.columns:
        if dataset[column].dtype == 'int64':
            columns.append(
                {
                    'name': rename_to_snake_case(column),
                    'type': 'number',
                    'options': {
                        'precision': 0
                    }
                }
            )
        elif dataset[column].dtype == 'float64':
            columns.append(
                {
                    'name': rename_to_snake_case(column),
                    'type': 'number',
                    'options': {
                        'precision': 2
                    }
                }
            )
        elif dataset[column].dtype == 'bool':
            columns.append(
                {
                    'name': rename_to_snake_case(column),
                    'type': 'checkbox'
                }
            )
        elif dataset[column].dtype == 'datetime64[ns]':
            columns.append(
                {
                    'name': rename_to_snake_case(column),
                    'type': 'dateTime',
                    'options': {
                        'dateFormat': {
                            'name': 'local',
                            'format': 'l'
                        },
                        'timeFormat': {
                            'name': '24hour',
                            'format': 'HH:mm'
                        },
                        'timeZone': 'client'
                    }
                }
            )
        else:
            columns.append(
                {
                    'name': rename_to_snake_case(column),
                    'type': 'singleLineText'
                }
            )
    return columns
