# pickle_handler.py
import pickle
from .base_table import Table
from .exceptions import FileOperationError

def load_table(filename: str, **kwargs) -> Table:
    """
    Загрузка таблицы из pickle файла
    
    Args:
        filename: имя файла
        **kwargs: дополнительные параметры для pickle.load
        
    Returns:
        Table: загруженная таблица
    """
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file, **kwargs)
            
            if isinstance(data, Table):
                return data
            elif isinstance(data, dict) and 'data' in data and 'headers' in data:
                return Table(data['data'], data['headers'])
            else:
                raise FileOperationError("Неподдерживаемый формат данных в pickle файле")
                
    except Exception as e:
        raise FileOperationError(f"Ошибка загрузки pickle: {e}")

def save_table(table: Table, filename: str, **kwargs) -> None:
    """
    Сохранение таблицы в pickle файл
    
    Args:
        table: таблица для сохранения
        filename: имя файла
        **kwargs: дополнительные параметры для pickle.dump
    """
    try:
        with open(filename, 'wb') as file:
            # Сохраняем как объект Table
            pickle.dump(table, file, **kwargs)
            
    except Exception as e:
        raise FileOperationError(f"Ошибка сохранения pickle: {e}")