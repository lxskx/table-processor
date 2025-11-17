# __init__.py
from .base_table import Table
from .csv_handler import load_table as load_csv, save_table as save_csv
from .pickle_handler import load_table as load_pickle, save_table as save_pickle
from .text_handler import save_table as save_text
from .table_operations import merge_tables

__all__ = [
    'Table',
    'load_csv', 'save_csv',
    'load_pickle', 'save_pickle', 
    'save_text',
    'merge_tables'
]