import os
from dotenv import load_dotenv
from loguru import logger
from treat_data import treat_data_pipeline
from send_to_airtable import send_to_airtable_pipeline

load_dotenv()

def main(file_path):
    SHEET_NAME = os.getenv('SHEET_NAME') if os.getenv('SHEET_NAME') else 0
    HEADER_ROW = int(os.getenv('HEADER_ROW') if os.getenv('HEADER_ROW') else 0)
    QUANTITY_COLUMNS = os.getenv('QUANTITY_COLUMNS').split(',') if os.getenv('QUANTITY_COLUMNS') else None
    DATE_COLUMNS = os.getenv('DATE_COLUMNS').split(',') if os.getenv('DATE_COLUMNS') else None
    COLUMNS_TO_SELECT = os.getenv('COLUMNS_TO_SELECT').split(',') if os.getenv('COLUMNS_TO_SELECT') else None
    COLUMNS_TO_HASH = os.getenv('COLUMNS_TO_HASH').split(',') if os.getenv('COLUMNS_TO_HASH') else None

    logger.info('Starting ETL process...')

    df = treat_data_pipeline(
        path=file_path,
        sheet_name=SHEET_NAME,
        header=HEADER_ROW,
        quantity_column=QUANTITY_COLUMNS,
        date_column=DATE_COLUMNS,
        columns_to_select=COLUMNS_TO_SELECT,
        columns_to_hash=COLUMNS_TO_HASH
    )

    send_to_airtable_pipeline(df)

if __name__ == '__main__':
    main()
