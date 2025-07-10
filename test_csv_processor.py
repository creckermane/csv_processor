import pytest
import tempfile
import os
import csv
from csv_processor import parse_where_condition, parse_aggregate, read_csv, apply_filter, apply_aggregation


# Создаем временный CSV-файл для тестов
@pytest.fixture
def sample_csv():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'brand', 'price', 'rating'])
        writer.writerow(['HOT 11S NFC', 'Infinix', '302', '4.9'])
        writer.writerow(['iphone 15 pro', 'apple', '999', '4.9'])
        writer.writerow(['galaxy s23 ultra', 'samsung', '1199', '4.8'])
        writer.writerow(['redmi note 12', 'xiaomi', '199', '4.6'])
        writer.writerow(['poco x5 pro', 'xiaomi', '299', '4.4'])
        f_path = f.name
    yield f_path
    os.unlink(f_path)


def test_read_csv(sample_csv):
    """Тестирование чтения CSV"""
    header, data = read_csv(sample_csv)
    assert header == ['name', 'brand', 'price', 'rating']
    assert len(data) == 4


def test_parse_where_condition():
    """Тестирование парсинга условия фильтрации"""
    assert parse_where_condition("price<305") == ("price", "<", "305")
    assert parse_where_condition("brand=samsung") == ("brand", "=", "samsung")
    assert parse_where_condition("rating>4.8") == ("rating", ">", "4.8")


def test_parse_aggregate():
    """Тестирование парсинга агрегации"""
    assert parse_aggregate("price:avg") == ("price", "avg")
    assert parse_aggregate("rating:max") == ("rating", "max")


def test_apply_filter_numeric():
    """Тестирование фильтрации по числовой колонке"""
    header = ['price']
    data = [['100'], ['200'], ['300']]
    condition = ("price", "<", "250")
    result = apply_filter(data, header, condition)
    assert result == [['100'], ['200']]


def test_apply_aggregation_avg():
    """Тестирование среднего значения"""
    header = ['price']
    data = [['100'], ['200'], ['300']]
    result = apply_aggregation(data, header, ("price", "avg"))
    assert result == [['price_avg', 200.0]]


def test_apply_aggregation_min_max():
    """Тестирование минимального и максимального значений"""
    header = ['price']
    data = [['100'], ['200'], ['1000']]
    assert apply_aggregation(data, header, ("price", "min")) == [['price_min', 100.0]]
    assert apply_aggregation(data, header, ("price", "max")) == [['price_max', 1000.0]]