# csv_handler.py
import csv
from typing import List, Any
from .base_table import Table
from .exceptions import FileOperationError

def load_table(filename: str, **kwargs) -> Table:
    """
    Загрузка таблицы из CSV файла
    
    Args:
        filename: имя файла
        **kwargs: дополнительные параметры для csv.reader
        
    Returns:
        Table: загруженная таблица
    """
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            # Определяем есть ли заголовки
            has_header = kwargs.pop('has_header', True)
            delimiter = kwargs.get('delimiter', ',')
            
            reader = csv.reader(file, **kwargs)
            rows = list(reader)
            
            if not rows:
                return Table()
                
            if has_header:
                headers = rows[0]
                data = rows[1:]
            else:
                headers = [f"col_{i}" for i in range(len(rows[0]))]
                data = rows
                
            return Table(data, headers)
            
    except Exception as e:
        raise FileOperationError(f"Ошибка загрузки CSV: {e}")

def save_table(table: Table, filename: str, **kwargs) -> None:
    """
    Сохранение таблицы в CSV файл
    
    Args:
        table: таблица для сохранения
        filename: имя файла
        **kwargs: дополнительные параметры для csv.writer
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, **kwargs)
            
            # Записываем заголовки
            if table.headers:
                writer.writerow(table.headers)
            
            # Записываем данные
            for row in table.data:
                writer.writerow(row)
                
    except Exception as e:
        raise FileOperationError(f"Ошибка сохранения CSV: {e}")