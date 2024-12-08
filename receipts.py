import os
import random
from datetime import datetime # дата (нужен для проставления информации о покупке в чеке)
import pytz # время (нужен для проставления информации о покупке в чеке)
from PIL import Image, ImageDraw, ImageFont # для отрисовки
from PyQt6.QtWidgets import QMessageBox


class ReceiptManager:
    def __init__(self):
        self.receipt_count = 1
        self.receipt_image_count = 1

    def generate_receipt(self, cart, total_price):
        """выводит .txt чек"""
        checkout_dir = os.path.join(os.path.dirname(__file__), "checkout")
        if not os.path.exists(checkout_dir):
            os.makedirs(checkout_dir)
        receipt_file_name = os.path.join(checkout_dir, f"receipt{self.receipt_count}.txt")
        self.receipt_count += 1
        moscow_tz = pytz.timezone("Europe/Moscow")
        moscow_time = datetime.now(moscow_tz)
        datetime_str = moscow_time.strftime("%d.%m.%Y %H:%M")
        receipt_lines = [
            "Чек покупки. Покупка совершена ({}):".format(datetime_str),
            "Статус - успешно",
            "",
            "Приобретенные товары:",
        ]
        receipt_lines += [
            f"{product} (x{quantity}): {price:.2f}₽" for product, quantity, price in cart
        ]
        receipt_lines.append("")
        receipt_lines.append(f"Общая сумма покупки: {total_price:.2f}₽")
        pleasant_phrases = [
            "Хорошего дня!",
            "Приятных покупок!",
            "Спасибо за покупку!",
            "Счастливого шопинга!",
            "Не забывайте о скидках!",
            "Возвращайтесь к нам!",
            "Пока!",
            "До новых встреч",
            "С наилучшими пожеланиями!",
            "Поздравляем с успешной покупкой!",
            "Удачных покупок!",
            "Всего хорошего!",
            "Всегда рады видеть вас!",
            "Приятного вечера!",
            "С любовью от нашей команды!",
            "Будьте счастливы!",
            "Замечательного дня!",
            "Покупайте с улыбкой!",
            "Улыбнитесь! Вы сделали хороший выбор!",
            "Купите то, что приносит радость!",
            "Не упустите свой шанс на скидки!",
            "Счастливых моментов с нашими товарами!",
            "Вы лучший покупатель!",
            "Рады вам помочь!",
            "Вы сделали отличный выбор!",
            "Удачи в шопинге!",
            "Счастья вам и вашим близким!",
            "Сделайте свою жизнь ярче!",
            "Пусть каждая покупка будет радостью!",
            "Замечательных покупок!",
            "Каждый день — новая возможность!",
            "Купите радость!",
        ]
        pleasant_phrase = random.choice(pleasant_phrases)
        receipt_lines.append(pleasant_phrase)
        with open(receipt_file_name, "w", encoding="utf-8") as file:
            file.write("\n".join(receipt_lines))
        image_path = os.path.join(checkout_dir, f"receipt_image{self.receipt_image_count}.png")
        self.receipt_image_count += 1
        self.create_receipt_image(receipt_lines, image_path)
        QMessageBox.information(None, "Чек сохранён", "Чек успешно создан!")

    def create_receipt_image(self, receipt_lines, image_path):
        '''рисует чек'''
        width, height = 400, 300 + len(receipt_lines) * 20
        background_color = (255, 255, 255)
        font_color = (0, 0, 0)
        font_path = "timesnewromanpsmt.ttf"
        font_size = 16
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            QMessageBox.warning(
                None, "Ошибка", "Файл шрифта не найден. Пожалуйста, проверьте путь к шрифту."
            )
            return
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Чек покупки", fill=font_color, font=font)
        y_text = 30
        for line in receipt_lines:
            line = line.replace("₽", "")
            draw.text((10, y_text), line, fill=font_color, font=font)
            y_text += 20
        image.save(image_path)