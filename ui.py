import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QListWidget,
    QMessageBox,
    QLineEdit,
    QGridLayout,
    QDialog,
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, QTimer
import pytz
from datetime import datetime
from receipts import ReceiptManager
from tables import load_admin_credentials, load_products


class SelfServiceKiosk(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Касса самообслуживания")
        self.setFixedSize(520, 900)
        self.set_background()
        self.layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)
        self.cart = []
        # Использование функций из tables.py
        self.admin_credentials = load_admin_credentials()
        (
            self.products,
            self.product_images,
            self.product_prices,
            self.product_units,
        ) = load_products()

        self.fixed_categories = {
            "Молочные продукты": "milk_produce.png",
            "Бакалея": "bakalei_produce.png",
            "Мясо": "meet_produce.png",
            "Напитки": "drink_produce.png",
            "Фрукты": "fruit_produce.png",
            "Овощи": "lagetables.png",
        }
        self.receipt_manager = ReceiptManager()  # Инициализация менеджера чеков
        self.payment_attempts = 0
        self.time_label = QLabel(self)
        self.time_label.setStyleSheet("color: white; font-size: 16px;")
        self.layout.addWidget(
            self.time_label,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.build_category_selection_page()
        self.build_cart_page()
        self.add_discount_button()
        self.stacked_widget.setCurrentIndex(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def set_background(self):
        background_image = QPixmap("main_screen/background.png")
        background_image = background_image.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )
        background_label = QLabel(self)
        background_label.setPixmap(background_image)
        background_label.setScaledContents(True)
        background_label.setGeometry(0, 0, self.width(), self.height())
        background_label.raise_()

    def build_category_selection_page(self):
        category_page = QWidget()
        layout = QVBoxLayout()
        top_label = QLabel("Выберите категорию\nтовара:")
        top_label.setStyleSheet("color: white; font-size: 40px;")
        top_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(top_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название товара...")
        self.search_input.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_input)
        self.category_buttons_widget = QWidget(category_page)
        buttons_layout = QGridLayout(self.category_buttons_widget)
        row, col = 0, 0
        for category, image_name in self.fixed_categories.items():
            btn = QPushButton()
            btn.setFixedSize(80, 80)
            btn.setIcon(QIcon(os.path.join("main_screen", image_name)))
            btn.setIconSize(QSize(90, 90))
            btn.clicked.connect(
                lambda checked, cat=category: self.show_product_selection(cat)
            )
            buttons_layout.addWidget(btn, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        go_to_cart_button = QPushButton("Корзина")
        go_to_cart_button.setFixedSize(85, 85)
        go_to_cart_button.setStyleSheet("background-color: black; color: white;")
        go_to_cart_button.clicked.connect(self.show_cart_page)
        buttons_layout.addWidget(go_to_cart_button, row, col)
        self.category_buttons_widget.setGeometry(
            0, 300, self.width(), buttons_layout.sizeHint().height()
        )
        layout.addWidget(self.category_buttons_widget)
        category_page.setLayout(layout)
        self.stacked_widget.addWidget(category_page)

    def add_discount_button(self):
        discount_button = QPushButton()
        discount_button.setStyleSheet("border: none;")
        discount_button.setIcon(QIcon(os.path.join("main_screen", "sells.png")))
        discount_button.setIconSize(QSize(520, 100))
        discount_button.clicked.connect(
            lambda: self.show_product_selection("Акция")
        )
        discount_button.setFixedHeight(100)
        self.layout.insertWidget(1, discount_button)

    def perform_search(self):
        """функция для поиска по названию"""
        search_query = self.search_input.text().lower().strip()
        if len(search_query) > 1:
            matched_products = [
                product
                for product in self.product_images.keys()
                if search_query in product.lower()
            ]
            if "Акция" in self.products:
                matched_products = [
                    product
                    for product in matched_products
                    if product not in self.products["Акция"]
                ]
            self.show_search_results(matched_products)
        else:
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, введите больше одной буквы."
            )

    def show_search_results(self, matched_products):
        """показ товаров из поиска (+проверка)"""
        self.search_result_page = QWidget()
        layout = QVBoxLayout(self.search_result_page)
        if matched_products:
            for product in matched_products:
                btn = QPushButton(product)
                btn.setMinimumSize(140, 180)
                btn.clicked.connect(lambda checked, prod=product: self.add_to_cart(prod))
                price_label = QLabel(f"{self.product_prices[product]:.2f}₽")
                price_label.setStyleSheet("color: black; font-size: 16px;")
                layout.addWidget(btn)
                layout.addWidget(price_label)
        else:
            no_result_label = QLabel("Нет информации о продукте.")
            no_result_label.setStyleSheet("color: white; font-size: 20px;")
            layout.addWidget(no_result_label)
        back_button = QPushButton("Назад к категориям")
        back_button.clicked.connect(self.show_category_selection_page)
        layout.addWidget(back_button)
        self.search_result_page.setLayout(layout)
        self.stacked_widget.addWidget(self.search_result_page)
        self.stacked_widget.setCurrentWidget(self.search_result_page)

    def show_product_selection(self, selected_category):
        if selected_category in self.products:
            self.current_category = selected_category
            self.products_list = self.products[selected_category]
            self.current_page = 0
            self.build_product_page()

    def build_product_page(self):
        """строит окна с отображением товаров из таблицы"""
        products = self.products_list
        page_size = 6
        pages_count = (len(products) + page_size - 1) // page_size
        product_page = QWidget()
        grid_layout = QGridLayout(product_page)
        start_index = self.current_page * page_size
        end_index = min(start_index + page_size, len(products))
        for index in range(start_index, end_index):
            product = products[index]
            btn = QPushButton(product)
            btn.setObjectName(product)
            btn.setMinimumSize(140, 180)
            image_path = self.product_images.get(product)
            current_dir = os.path.dirname(os.path.realpath(__file__))
            full_image_path = os.path.join(current_dir, image_path)
            pixmap = QPixmap(full_image_path) if os.path.exists(full_image_path) else None
            if not pixmap or pixmap.isNull():
                QMessageBox.warning(self, "Ошибка", f"Изображение для {product} не найдено.")
                pixmap = QPixmap(140, 140)
                pixmap.fill(Qt.GlobalColor.red)
            pixmap = pixmap.scaled(140, 140)
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn.clicked.connect(lambda checked, prod=product: self.add_to_cart(prod))
            price_label = QLabel(f"{self.product_prices[product]:.2f}₽")
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            price_label.setStyleSheet("color: black; font-size: 16px;")
            layout = QVBoxLayout()
            layout.addWidget(label)
            layout.addWidget(btn)
            layout.addWidget(price_label)
            container = QWidget()
            container.setLayout(layout)
            grid_layout.addWidget(container, index // 3, index % 3)
        navigation_layout = QVBoxLayout()
        if self.current_page > 0:
            back_button = QPushButton("Назад")
            back_button.clicked.connect(self.prev_page)
            navigation_layout.addWidget(back_button)
        if self.current_page < pages_count - 1:
            forward_button = QPushButton("Вперед")
            forward_button.clicked.connect(self.next_page)
            navigation_layout.addWidget(forward_button)
        back_to_categories_button = QPushButton("Назад к категориям")
        back_to_categories_button.clicked.connect(self.show_category_selection_page)
        navigation_layout.addWidget(back_to_categories_button)
        grid_layout.addLayout(navigation_layout, end_index // 3 + 1, 0, 1, 3)
        product_page.setLayout(grid_layout)
        self.stacked_widget.addWidget(product_page)
        self.stacked_widget.setCurrentWidget(product_page)

    def next_page(self):
        self.current_page += 1
        self.build_product_page()

    def prev_page(self):
        self.current_page -= 1
        self.build_product_page()

    def add_to_cart(self, product):
        """ Добавление в корзину (+проверка на кг) """
        unit = self.product_units[product]
        if unit == "кг":
            self.prompt_weight_input(product)
        else:
            self.add_product_to_cart(product)

    def prompt_weight_input(self, product):
        """ Если проверка на кг успешна """
        weight_dialog = QDialog(self)
        weight_dialog.setWindowTitle("Введите вес товара")
        weight_dialog.setFixedSize(300, 150)

        weight_layout = QVBoxLayout(weight_dialog)
        weight_label = QLabel("Введите вес в килограммах:")
        weight_input = QLineEdit()
        weight_input.setPlaceholderText("Пример: 1.5")

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(
            lambda: self.process_weight_input(weight_input.text(), product, weight_dialog)
        )

        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(weight_input)
        weight_layout.addWidget(ok_button)

        weight_dialog.setLayout(weight_layout)
        weight_dialog.exec()

    def process_weight_input(self, weight_str, product, dialog):
        """ Процесс ввода веса (проверка на правильность ввода и комментарии по вводу) """
        try:
            weight = float(weight_str)
            if weight <= 0:
                raise ValueError("Вес должен быть положительным.")
            self.cart.append((product, weight, self.product_prices[product] * weight))
            QMessageBox.information(
                self, "Добавлено в корзину",
                f"{product} добавлен в корзину с весом {weight:.2f} кг!"
            )
            dialog.accept()
            self.update_cart_display()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное значение веса.")

    def add_product_to_cart(self, product):
        """ Информация пользователю про добавление товара в корзину (если товар уже был, то просто увеличение его значения) """
        for index, (cart_product, quantity, price) in enumerate(self.cart):
            if cart_product == product:
                self.cart[index] = (cart_product, quantity + 1, price)
                QMessageBox.information(
                    self, "Добавлено в корзину",
                    f"{product} количество увеличено на 1!"
                )
                self.update_cart_display()
                return
        self.cart.append((product, 1, self.product_prices[product]))
        QMessageBox.information(self, "Добавлено в корзину", f"{product} добавлен в корзину!")

    def build_cart_page(self):
        """ Построение таблицы (используем QListWidget) """
        self.cart_page = QListWidget()
        self.update_cart_display()
        remove_button = QPushButton("Удалить товар")
        remove_button.clicked.connect(self.prompt_remove_product)
        checkout_button = QPushButton("Оформить заказ")
        checkout_button.clicked.connect(self.checkout)
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_category_selection_page)
        layout = QVBoxLayout()
        cart_label = QLabel("Содержимое корзины:")
        cart_label.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(cart_label)
        layout.addWidget(self.cart_page)
        layout.addWidget(remove_button)
        layout.addWidget(checkout_button)
        layout.addWidget(back_button)
        cart_container = QWidget()
        cart_container.setLayout(layout)
        self.stacked_widget.addWidget(cart_container)

    def update_cart_display(self):
        self.cart_page.clear()
        for product, quantity, price in self.cart:
            self.cart_page.addItem(f"{product}: {price:.2f}₽")

    def show_cart_page(self):
        self.update_cart_display()
        self.stacked_widget.setCurrentIndex(1)

    def prompt_remove_product(self):
        item = self.cart_page.currentItem()
        if item:
            product_info = item.text().split(":")[0].strip()
            self.show_admin_login_dialog(product_info)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления из корзины.")

    def show_admin_login_dialog(self, product):
        """ Окно для ввода данных администратора """
        dialog = QDialog(self)
        dialog_layout = QVBoxLayout(dialog)
        username_input = QLineEdit()
        username_input.setPlaceholderText("Логин администратора")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Пароль администратора")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("Войти")
        login_button.clicked.connect(
            lambda: self.check_login_credentials(
                username_input.text(), password_input.text(), product, dialog
            )
        )
        dialog_layout.addWidget(username_input)
        dialog_layout.addWidget(password_input)
        dialog_layout.addWidget(login_button)
        dialog.setLayout(dialog_layout)
        dialog.setWindowTitle("Вход администратора")
        dialog.exec()

    def check_login_credentials(self, username, password, product, dialog):
        """ Проверка данных администратора """
        if username in self.admin_credentials and self.admin_credentials[username] == password:
            self.remove_from_cart(product)
            dialog.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль. Попробуйте снова.")

    def remove_from_cart(self, product):
        """ Логика удаления товара из корзины (проверка на количество товара и кг) """
        product_to_remove = product.lower()
        for index, (cart_product, quantity, price) in enumerate(self.cart):
            if cart_product.lower() == product_to_remove:
                unit = self.product_units.get(cart_product)
                if unit == "кг":
                    del self.cart[index]
                    QMessageBox.information(self, "Удалено из корзины", f"{cart_product} удалён из корзины.")
                else:
                    if quantity > 1:
                        self.cart[index] = (cart_product, quantity - 1, price)
                        QMessageBox.information(
                            self, "Удалено из корзины",
                            f"{cart_product} количество уменьшено на 1!"
                        )
                    else:
                        del self.cart[index]
                        QMessageBox.information(self, "Удалено из корзины", f"{cart_product} удалён из корзины.")
                self.update_cart_display()
                return
        QMessageBox.warning(self, "Ошибка", f'Товар "{product}" не найден в корзине.')

    def show_category_selection_page(self):
        self.search_input.clear()
        self.stacked_widget.setCurrentIndex(0)

    def calculate_total(self):
        return sum(price * quantity for _, quantity, price in self.cart)

    def checkout(self):
        self.show_payment_dialog()

    def show_payment_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ожидание подтверждения оплаты от платежной системы")
        dialog.setFixedSize(400, 200)
        layout = QVBoxLayout()
        message_label = QLabel("Ожидаем подтверждение оплаты...")
        layout.addWidget(message_label)

        def process_payment_status():
            status = input("true - для подтверждения операции - ")
            if status.lower() == "true":
                self.process_payment()
                dialog.accept()
            else:
                self.payment_attempts += 1
                QMessageBox.warning(
                    self, "Подтверждение", "Оплата отклонена. Пожалуйста, попробуйте снова."
                )
                if self.payment_attempts >= 3:
                    QMessageBox.warning(
                        self,
                        "Слишком много попыток",
                        "Оплата не была успешно подтверждена 3 раза. Окно будет закрыто.",
                    )
                    dialog.accept()
                else:
                    dialog.reject()

        QTimer.singleShot(100, process_payment_status)
        dialog.setLayout(layout)
        dialog.finished.connect(
            lambda result: self.show_payment_dialog()
            if result == QDialog.DialogCode.Rejected and self.payment_attempts < 3
            else None
        )
        dialog.exec()

    def process_payment(self):
        """ Процесс оплаты """
        if not self.cart:
            QMessageBox.warning(self, "Корзина пуста", "Ваша корзина пуста!")
            return
        total_price = self.calculate_total()
        self.receipt_manager.generate_receipt(self.cart, total_price)  # Вызов метода из нового файла
        QMessageBox.information(
            self, "Оформление заказа", f'Ваш заказ оформлен! Общая сумма вашего заказа: {total_price:.2f}₽'
        )
        self.cart.clear()
        self.update_cart_display()

    def update_time(self):
        """ Вывод времени """
        moscow_tz = pytz.timezone("Europe/Moscow")
        moscow_time = datetime.now(moscow_tz)
        self.time_label.setText(moscow_time.strftime("%H:%M:%S"))
