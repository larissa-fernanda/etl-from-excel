import os
import pytest
from unittest.mock import patch, MagicMock
from etl_from_excel.etl import main

@patch('etl_from_excel.etl.treat_data_pipeline')
@patch('etl_from_excel.etl.send_to_airtable_pipeline')
def test_etl_pipeline(mock_send_to_airtable, mock_treat_data_pipeline):
    """
    Test the main function of the ETL pipeline.
    It should call the treat_data_pipeline and send_to_airtable_pipeline functions with the correct parameters.
    """
    mock_df = MagicMock()
    mock_treat_data_pipeline.return_value = mock_df

    os.environ['SHEET_NAME'] = 'Sheet1'
    os.environ['HEADER_ROW'] = '1'
    os.environ['QUANTITY_COLUMNS'] = 'Quantidade'
    os.environ['DATE_COLUMNS'] = 'Data'
    os.environ['COLUMNS_TO_SELECT'] = 'Data,Quantidade,Produto'
    os.environ['COLUMNS_TO_HASH'] = 'Data,Produto'

    file_path = 'fake_path.xlsx'
    main(file_path)

    mock_treat_data_pipeline.assert_called_once_with(
        path=file_path,
        sheet_name='Sheet1',
        header=1,
        quantity_column=['Quantidade'],
        date_column=['Data'],
        columns_to_select=['Data', 'Quantidade', 'Produto'],
        columns_to_hash=['Data', 'Produto']
    )

    mock_send_to_airtable.assert_called_once_with(mock_df)
