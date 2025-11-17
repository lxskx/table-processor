class TableError(Exception):
    """Базовое исключение для работы с таблицами"""
    pass

class FileOperationError(TableError):
    """Ошибка при работе с файлами"""
    pass

class ColumnError(TableError):
    """Ошибка связанная со столбцами"""
    pass

class RowError(TableError):
    """Ошибка связанная со строками"""
    pass

class OperationError(TableError):
    """Ошибка при выполнении операций"""
    pass

class MergeError(TableError):
    """Ошибка при слиянии таблиц"""
    pass