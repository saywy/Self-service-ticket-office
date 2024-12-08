import csv
import gspread
from gspread import Client, Spreadsheet

SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1OiZy-fRYNQSTZMPY0EpY1GxvzWyWsIBABVmLEvETMP0/edit?gid=0#gid=0"
)


def load_admin_credentials():
    """Подгрузка данных адинов"""
    credentials = {}
    try:
        with open("admin_credentials.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    credentials[row[0]] = row[1]
    except FileNotFoundError:
        raise FileNotFoundError("Файл с учетными данными администраторов не найден.")
    return credentials


def load_products():
    """ Подгрузка информации из гугла таблицы в отельные словари"""
    gc: Client = gspread.service_account("./service_account.json")
    sh: Spreadsheet = gc.open_by_url(SPREADSHEET_URL)
    ws = sh.sheet1
    data = ws.get_all_records()
    products_per_category = {}
    product_images = {}
    product_prices = {}
    product_units = {}
    for row in data:
        category = row["Отдел"]
        product_name = row["Наименование товара"]
        product_article = row["Артикул"]
        price = row["Цена за штуку"]
        unit = row["Ед. измерения"]
        image_path = f"food/{product_article}.png"
        if category not in products_per_category:
            products_per_category[category] = []
        products_per_category[category].append(product_name)
        product_images[product_name] = image_path
        product_prices[product_name] = price
        product_units[product_name] = unit
    return (
        products_per_category,
        product_images,
        product_prices,
        product_units,
    )
# возвращает каждый словарь