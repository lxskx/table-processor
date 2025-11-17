# base_table.py
from typing import List, Dict, Any, Union, Optional
from .exceptions import *

class Table:
    def __init__(self, data: Optional[List[List[Any]]] = None, 
                 headers: Optional[List[str]] = None,
                 index_col: Optional[str] = None):
        self._data = data or []
        self._headers = headers or []
        self._index_col = index_col
        self._column_types: Dict[Union[int, str], type] = {}
        self._detect_column_types()
    
    def _detect_column_types(self) -> None:
        if not self._data or not self._headers:
            return
            
        for col_idx, header in enumerate(self._headers):
            values = [row[col_idx] for row in self._data if col_idx < len(row)]
            if not values:
                self._column_types[col_idx] = str
                self._column_types[header] = str
                continue
                
            sample_value = values[0]
            if isinstance(sample_value, (int, float, bool, str)):
                detected_type = type(sample_value)
            else:
                detected_type = str
                
            self._column_types[col_idx] = detected_type
            self._column_types[header] = detected_type
    
    def _convert_value(self, value: Any, col: Union[int, str]) -> Any:
        col_type = self._column_types.get(col, str)
        try:
            if col_type == bool:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'y')
                return bool(value)
            elif col_type == int:
                return int(value)
            elif col_type == float:
                return float(value)
            elif col_type == str:
                return str(value)
            else:
                return value
        except (ValueError, TypeError):
            raise OperationError(f"Не удалось преобразовать {value} к типу {col_type}")
    
    def get_rows_by_number(self, start: int, stop: Optional[int] = None, 
                          copy_table: bool = False) -> 'Table':
        if not self._data:
            raise RowError("Таблица пуста")
            
        if start < 0 or start >= len(self._data):
            raise RowError(f"Некорректный начальный индекс: {start}")
            
        if stop is not None and (stop < start or stop > len(self._data)):
            raise RowError(f"Некорректный конечный индекс: {stop}")
            
        if stop is None:
            selected_data = [self._data[start]]
        else:
            selected_data = self._data[start:stop]
            
        if copy_table:
            import copy
            new_data = copy.deepcopy(selected_data)
            new_headers = copy.deepcopy(self._headers)
            new_types = copy.deepcopy(self._column_types)
            new_table = Table(new_data, new_headers, self._index_col)
            new_table._column_types = new_types
            return new_table
        else:
            return Table(selected_data, self._headers, self._index_col)
    
    def get_rows_by_index(self, *indices: Any, copy_table: bool = False) -> 'Table':
        if not self._data:
            raise RowError("Таблица пуста")
            
        if not self._index_col:
            raise RowError("Индексный столбец не задан")
            
        index_col_idx = self._get_column_index(self._index_col)
        selected_data = []
        
        for row in self._data:
            if index_col_idx < len(row) and row[index_col_idx] in indices:
                selected_data.append(row)
                
        if copy_table:
            import copy
            new_data = copy.deepcopy(selected_data)
            new_headers = copy.deepcopy(self._headers)
            new_types = copy.deepcopy(self._column_types)
            new_table = Table(new_data, new_headers, self._index_col)
            new_table._column_types = new_types
            return new_table
        else:
            return Table(selected_data, self._headers, self._index_col)
    
    def _get_column_index(self, column: Union[int, str]) -> int:
        if isinstance(column, int):
            if column < 0 or column >= len(self._headers):
                raise ColumnError(f"Некорректный индекс столбца: {column}")
            return column
        else:
            if column not in self._headers:
                raise ColumnError(f"Столбец '{column}' не найден")
            return self._headers.index(column)
    
    def get_column_types(self, by_number: bool = True) -> Dict[Union[int, str], type]:
        result = {}
        for key, value in self._column_types.items():
            if by_number and isinstance(key, int):
                result[key] = value
            elif not by_number and isinstance(key, str):
                result[key] = value
        return result
    
    def set_column_types(self, types_dict: Dict[Union[int, str], type], 
                        by_number: bool = True) -> None:
        for col, col_type in types_dict.items():
            if col_type not in (int, float, bool, str):
                raise ColumnError(f"Неподдерживаемый тип: {col_type}")
                
            if by_number:
                if not isinstance(col, int) or col < 0 or col >= len(self._headers):
                    raise ColumnError(f"Некорректный номер столбца: {col}")
                self._column_types[col] = col_type
                if col < len(self._headers):
                    self._column_types[self._headers[col]] = col_type
            else:
                if not isinstance(col, str) or col not in self._headers:
                    raise ColumnError(f"Некорректное имя столбца: {col}")
                self._column_types[col] = col_type
                self._column_types[self._headers.index(col)] = col_type
        
        self._convert_existing_data()
    
    def _convert_existing_data(self) -> None:
        for row in self._data:
            for col_idx in range(min(len(row), len(self._headers))):
                col_header = self._headers[col_idx]
                try:
                    row[col_idx] = self._convert_value(row[col_idx], col_header)
                except OperationError:
                    pass
    
    def get_values(self, column: Union[int, str] = 0) -> List[Any]:
        col_idx = self._get_column_index(column)
        values = []
        for row in self._data:
            if col_idx < len(row):
                values.append(self._convert_value(row[col_idx], column))
        return values
    
    def get_value(self, column: Union[int, str] = 0) -> Any:
        if len(self._data) != 1:
            raise RowError("Метод get_value применим только к таблицам с одной строкой")
        return self.get_values(column)[0]
    
    def set_values(self, values: List[Any], column: Union[int, str] = 0) -> None:
        col_idx = self._get_column_index(column)
        
        if len(values) != len(self._data):
            raise OperationError("Количество значений должно совпадать с количеством строк")
        
        for i, value in enumerate(values):
            if i < len(self._data) and col_idx < len(self._data[i]):
                self._data[i][col_idx] = self._convert_value(value, column)
    
    def set_value(self, value: Any, column: Union[int, str] = 0) -> None:
        if len(self._data) != 1:
            raise RowError("Метод set_value применим только к таблицам с одной строкой")
        self.set_values([value], column)

    # АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ
    def _arithmetic_operation(self, other: Any, operation: str, column: Union[int, str] = 0) -> 'Table':
        col_idx = self._get_column_index(column)
        result_values = []
        
        for row in self._data:
            if col_idx >= len(row):
                result_values.append(None)
                continue
                
            try:
                left_val = row[col_idx]
                
                if operation == 'add':
                    result = left_val + other
                elif operation == 'sub':
                    result = left_val - other
                elif operation == 'mul':
                    result = left_val * other
                elif operation == 'div':
                    if other == 0:
                        raise OperationError("Деление на ноль")
                    result = left_val / other
                else:
                    raise OperationError(f"Неизвестная операция: {operation}")
                    
                result_values.append(result)
            except (TypeError, ValueError) as e:
                raise OperationError(f"Ошибка при выполнении операции: {e}")
        
        result_data = [[val] for val in result_values]
        result_headers = [f"result_{operation}"]
        return Table(result_data, result_headers)
    
    def add(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        return self._arithmetic_operation(other, 'add', column)
    
    def sub(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        return self._arithmetic_operation(other, 'sub', column)
    
    def mul(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        return self._arithmetic_operation(other, 'mul', column)
    
    def div(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        return self._arithmetic_operation(other, 'div', column)
    
    # ОПЕРАЦИИ СРАВНЕНИЯ
    def _comparison_operation(self, other: Any, operation: str, column: Union[int, str] = 0) -> List[bool]:
        col_idx = self._get_column_index(column)
        result = []
        
        for row in self._data:
            if col_idx >= len(row):
                result.append(False)
                continue
                
            try:
                left_val = row[col_idx]
                
                if operation == 'eq':
                    result.append(left_val == other)
                elif operation == 'ne':
                    result.append(left_val != other)
                elif operation == 'gr':
                    result.append(left_val > other)
                elif operation == 'ls':
                    result.append(left_val < other)
                elif operation == 'ge':
                    result.append(left_val >= other)
                elif operation == 'le':
                    result.append(left_val <= other)
                else:
                    raise OperationError(f"Неизвестная операция сравнения: {operation}")
            except (TypeError, ValueError) as e:
                raise OperationError(f"Ошибка при сравнении: {e}")
        
        return result
    
    def eq(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'eq', column)
    
    def ne(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'ne', column)
    
    def gr(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'gr', column)
    
    def ls(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'ls', column)
    
    def ge(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'ge', column)
    
    def le(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        return self._comparison_operation(other, 'le', column)
    
    def filter_rows(self, bool_list: List[bool], copy_table: bool = False) -> 'Table':
        if len(bool_list) != len(self._data):
            raise RowError("Длина bool_list должна совпадать с количеством строк")
        
        filtered_data = [row for i, row in enumerate(self._data) if bool_list[i]]
        
        if copy_table:
            import copy
            new_data = copy.deepcopy(filtered_data)
            new_headers = copy.deepcopy(self._headers)
            new_types = copy.deepcopy(self._column_types)
            new_table = Table(new_data, new_headers, self._index_col)
            new_table._column_types = new_types
            return new_table
        else:
            return Table(filtered_data, self._headers, self._index_col)
    
        # ДОБАВЬ ЭТО ПРЯМО В КЛАСС - ПОСЛЕ set_value И ДО print_table

    def add(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        """Сложение +"""
        col_idx = self._get_column_index(column)
        result_values = []
        
        for row in self._data:
            if col_idx >= len(row):
                result_values.append(None)
                continue
            result_values.append(row[col_idx] + other)
        
        result_data = [[val] for val in result_values]
        return Table(result_data, ["result_add"])

    def sub(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        """Вычитание -"""
        col_idx = self._get_column_index(column)
        result_values = []
        
        for row in self._data:
            if col_idx >= len(row):
                result_values.append(None)
                continue
            result_values.append(row[col_idx] - other)
        
        result_data = [[val] for val in result_values]
        return Table(result_data, ["result_sub"])

    def mul(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        """Умножение *"""
        col_idx = self._get_column_index(column)
        result_values = []
        
        for row in self._data:
            if col_idx >= len(row):
                result_values.append(None)
                continue
            result_values.append(row[col_idx] * other)
        
        result_data = [[val] for val in result_values]
        return Table(result_data, ["result_mul"])

    def div(self, other: Any, column: Union[int, str] = 0) -> 'Table':
        """Деление /"""
        if other == 0:
            raise OperationError("Деление на ноль")
        col_idx = self._get_column_index(column)
        result_values = []
        
        for row in self._data:
            if col_idx >= len(row):
                result_values.append(None)
                continue
            result_values.append(row[col_idx] / other)
        
        result_data = [[val] for val in result_values]
        return Table(result_data, ["result_div"])

    def gr(self, other: Any, column: Union[int, str] = 0) -> List[bool]:
        """Больше >"""
        col_idx = self._get_column_index(column)
        result = []
        
        for row in self._data:
            if col_idx >= len(row):
                result.append(False)
                continue
            result.append(row[col_idx] > other)
        
        return result
    
    def print_table(self) -> None:
        if not self._headers and not self._data:
            print("Пустая таблица")
            return
            
        col_widths = []
        for i, header in enumerate(self._headers):
            max_width = len(str(header))
            for row in self._data:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
        
        header_line = ""
        for i, header in enumerate(self._headers):
            header_line += f"{header:<{col_widths[i]}}"
        print(header_line)
        print("-" * len(header_line))
        
        for row in self._data:
            row_line = ""
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f"{str(cell):<{col_widths[i]}}"
            print(row_line)
    
    @property
    def data(self) -> List[List[Any]]:
        return self._data
    
    @property
    def headers(self) -> List[str]:
        return self._headers
    
    @property
    def shape(self) -> tuple:
        rows = len(self._data)
        cols = len(self._headers) if self._headers else (len(self._data[0]) if self._data else 0)
        return (rows, cols)