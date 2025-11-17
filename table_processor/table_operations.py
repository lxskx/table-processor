# table_operations.py
from typing import List
from .base_table import Table
from .exceptions import MergeError

def merge_tables(table1: Table, table2: Table, by_number: bool = True, 
                how: str = 'inner') -> Table:
    """
    Слияние двух таблиц
    
    Args:
        table1: первая таблица
        table2: вторая таблица
        by_number: использовать номера строк (True) или значения индекса (False)
        how: тип слияния ('inner', 'left', 'right', 'outer')
    
    Returns:
        Table: объединенная таблица
    """
    if how not in ('inner', 'left', 'right', 'outer'):
        raise MergeError(f"Неподдерживаемый тип слияния: {how}")
    
    # Собираем все уникальные заголовки
    all_headers = list(table1.headers)
    for header in table2.headers:
        if header not in all_headers:
            all_headers.append(header)
    
    result_data = []
    
    if by_number:
        # Слияние по номерам строк
        max_rows = max(len(table1.data), len(table2.data))
        
        for i in range(max_rows):
            row_dict = {}
            
            # Данные из первой таблицы
            if i < len(table1.data):
                for j, header in enumerate(table1.headers):
                    if j < len(table1.data[i]):
                        row_dict[header] = table1.data[i][j]
            
            # Данные из второй таблицы
            if i < len(table2.data):
                for j, header in enumerate(table2.headers):
                    if j < len(table2.data[i]):
                        row_dict[header] = table2.data[i][j]
            
            # Проверяем условия для включения строки
            include_row = False
            if how == 'inner':
                include_row = (i < len(table1.data) and i < len(table2.data))
            elif how == 'left':
                include_row = (i < len(table1.data))
            elif how == 'right':
                include_row = (i < len(table2.data))
            elif how == 'outer':
                include_row = True
            
            if include_row:
                result_row = [row_dict.get(header, '') for header in all_headers]
                result_data.append(result_row)
    
    else:
        # Слияние по значениям индекса
        if not table1._index_col or not table2._index_col:
            raise MergeError("Для слияния по индексу обе таблицы должны иметь индексный столбец")
        
        # Создаем словари для быстрого доступа
        table1_dict = {}
        idx_col1 = table1.headers.index(table1._index_col)
        for row in table1.data:
            if idx_col1 < len(row):
                table1_dict[row[idx_col1]] = row
        
        table2_dict = {}
        idx_col2 = table2.headers.index(table2._index_col)
        for row in table2.data:
            if idx_col2 < len(row):
                table2_dict[row[idx_col2]] = row
        
        # Определяем ключи для слияния
        keys1 = set(table1_dict.keys())
        keys2 = set(table2_dict.keys())
        
        if how == 'inner':
            merge_keys = keys1 & keys2
        elif how == 'left':
            merge_keys = keys1
        elif how == 'right':
            merge_keys = keys2
        elif how == 'outer':
            merge_keys = keys1 | keys2
        
        # Собираем результат
        for key in sorted(merge_keys):
            row_dict = {}
            
            # Данные из первой таблицы
            if key in table1_dict:
                for j, header in enumerate(table1.headers):
                    if j < len(table1_dict[key]):
                        row_dict[header] = table1_dict[key][j]
            
            # Данные из второй таблицы
            if key in table2_dict:
                for j, header in enumerate(table2.headers):
                    if j < len(table2_dict[key]):
                        row_dict[header] = table2_dict[key][j]
            
            result_row = [row_dict.get(header, '') for header in all_headers]
            result_data.append(result_row)
    
    return Table(result_data, all_headers)