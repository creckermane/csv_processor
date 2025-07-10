import argparse  # Для обработки аргументов командной строки
import csv       # Для работы с CSV-файлами
from tabulate import tabulate  # Для красивого вывода таблиц в консоль


def parse_where_condition(condition: str):
    """
    Парсит условие фильтрации. Пример: "price<500" -> ("price", "<", "500")
    Поддерживает операторы: >, <, =
    """
    if not condition:
        return None
    # Проверяем наличие одного из допустимых операторов
    for op in [">", "<", "="]:
        if op in condition:
            column, value = condition.split(op)
            return column.strip(), op.strip(), value.strip()
    raise ValueError(f"Неверный формат условия фильтрации: {condition}")


def parse_aggregate(aggregate: str):
    """
    Парсит параметр агрегации. Пример: "price:avg" -> ("price", "avg")
    Допустимые функции агрегации: avg, min, max
    """
    if not aggregate:
        return None
    parts = aggregate.split(":")
    if len(parts) != 2 or parts[1] not in ["avg", "min", "max"]:
        raise ValueError(f"Неверный формат агрегации: {aggregate}")
    return parts[0].strip(), parts[1].strip()


def apply_filter(data, header, condition):
    """
    Применяет фильтр к данным на основе условия.
    Может работать как с числовыми, так и с текстовыми значениями.
    """
    if not condition:
        return data  # Если нет условия — возвращаем исходные данные

    col_name, op, value = condition
    col_index = header.index(col_name)  # Номер колонки по имени

    try:
        # Пробуем привести значение к float (число)
        converted_value = float(value)
        is_numeric = True
    except ValueError:
        # Если не число — оставляем как строку
        converted_value = value
        is_numeric = False

    filtered = []
    for row in data:
        cell_value = row[col_index]
        try:
            # Пытаемся привести значение ячейки к числу
            cell_float = float(cell_value)
            if is_numeric:
                # Сравнение чисел
                if op == ">" and cell_float > converted_value:
                    filtered.append(row)
                elif op == "<" and cell_float < converted_value:
                    filtered.append(row)
                elif op == "=" and cell_float == converted_value:
                    filtered.append(row)
            else:
                # Если значение не число, но сравниваемое тоже не число — проверяем точное совпадение
                if op == "=" and cell_value == converted_value:
                    filtered.append(row)
        except ValueError:
            # Если не удалось привести к числу, но это не требуется — просто проверяем равенство
            if op == "=" and cell_value == converted_value:
                filtered.append(row)
    return filtered


def apply_aggregation(data, header, aggregation):
    """
    Применяет агрегацию к числовой колонке. Возвращает одно значение в виде таблицы.
    Например: [['price_avg', 200.0]]
    """
    if not aggregation:
        return None

    col_name, func = aggregation
    try:
        col_index = header.index(col_name)
        values = [float(row[col_index]) for row in data]  # Преобразуем все значения к float

        if func == "avg":
            result = sum(values) / len(values)
        elif func == "min":
            result = min(values)
        elif func == "max":
            result = max(values)

        return [[col_name + "_" + func, result]]  # Результат в табличном виде
    except Exception as e:
        raise ValueError(f"Ошибка при агрегации: {e}")


def read_csv(path):
    """
    Читает CSV-файл, возвращает заголовок и данные.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Первая строка — заголовок
        rows = [row for row in reader]  # Остальные строки — данные
        return header, rows


def main():
    """
    Главная функция. Обрабатывает аргументы командной строки,
    применяет фильтрацию и агрегацию, выводит результат.
    """

    # Парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Обработка CSV-файлов.")
    parser.add_argument("--path", required=True, help="Путь к CSV-файлу")
    parser.add_argument("--where", help="Условие фильтрации (например, price<500)")
    parser.add_argument("--aggregate", help="Функция агрегации (например, price:avg)")

    args = parser.parse_args()

    # Чтение данных из CSV
    header, data = read_csv(args.path)

    # Применение фильтра
    data = apply_filter(data, header, parse_where_condition(args.where))

    # Применение агрегации
    result_table = apply_aggregation(data, header, parse_aggregate(args.aggregate))

    # Вывод результата
    if result_table:
        print(tabulate(result_table, headers="keys", tablefmt="psql"))
    else:
        print(tabulate(data, headers=header, tablefmt="psql"))


if __name__ == "__main__":
    main()