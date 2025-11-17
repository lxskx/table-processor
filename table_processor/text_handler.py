# text_handler.py
from .base_table import Table
from .exceptions import FileOperationError

def save_table(table: Table, filename: str, **kwargs) -> None:
    """
    Сохранение таблицы в текстовый файл
    
    Args:
        table: таблица для сохранения
        filename: имя файла
        **kwargs: дополнительные параметры
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            # Сохраняем таблицу в том же формате, что и print_table()
            if not table.headers and not table.data:
                file.write("Пустая таблица\n")
                return
            
            # Определяем ширину столбцов
            col_widths = []
            for i, header in enumerate(table.headers):
                max_width = len(str(header))
                for row in table.data:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                col_widths.append(max_width + 2)
            
            # Записываем заголовки
            header_line = ""
            for i, header in enumerate(table.headers):
                header_line += f"{header:<{col_widths[i]}}"
            file.write(header_line + "\n")
            file.write("-" * len(header_line) + "\n")
            
            # Записываем данные
            for row in table.data:
                row_line = ""
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        row_line += f"{str(cell):<{col_widths[i]}}"
                file.write(row_line + "\n")
                
    except Exception as e:
        raise FileOperationError(f"Ошибка сохранения текстового файла: {e}")