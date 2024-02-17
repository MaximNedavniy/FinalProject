from PyQt5 import QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QRegExpValidator
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView

import API
from form_binance import Ui_Form
from form_new_entry_db import Ui_new_entry_db
import sys
from database_ import Database


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.database = Database(
            dbname='crypto_db',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432')
        self.ui.refreshButton.clicked.connect(self.update_data)
        self.ui.exitButton_4.clicked.connect(self.close)
        self.ui.addDBButton.clicked.connect(self.show_new_entry_window)
        self.ui.deleteDBButton.clicked.connect(self.delete_selected_row)
        self.ui.tableWidget.itemSelectionChanged.connect(
            self.update_button_state)
        self.populate_table()
        self.ui.total_balance.setVisible(False)
        self.ui.total_pnl.setVisible(False)

    def update_data(self):
        with self.database as db:
            data = API.get_price_and_percent24h(db.get_list_db())
            if len(data) != 0:
                self.ui.refreshButton.setEnabled(True)
                self.ui.tableWidget_2.setRowCount(len(data))
                self.ui.tableWidget_2.setColumnCount(4)
                self.ui.tableWidget_2.clear()
                self.ui.tableWidget_2.horizontalHeader().setVisible(True)
                self.ui.tableWidget_2.setHorizontalHeaderItem(
                    0, QTableWidgetItem("Назва"))
                self.ui.tableWidget_2.setHorizontalHeaderItem(
                    1, QTableWidgetItem("Поточна ціна"))
                self.ui.tableWidget_2.setHorizontalHeaderItem(
                    2, QTableWidgetItem("% (24h)"))
                self.ui.tableWidget_2.setHorizontalHeaderItem(
                    3, QTableWidgetItem("PNL"))
                total_balance = []
                total_pnl = []
                for row_num, (currency_pair, data) in enumerate(data.items()):
                    # Додаємо назву валютної пари в першу колонку
                    currency_item = QTableWidgetItem(currency_pair)
                    self.ui.tableWidget_2.setItem(row_num, 0, currency_item)

                    # Додаємо ціну в другу колонку
                    price_item = QTableWidgetItem(str(data['price']))
                    self.ui.tableWidget_2.setItem(row_num, 1, price_item)

                    # Додаємо зміну відсотків в третю колонку
                    percent_change_item = QTableWidgetItem(
                        str(f"{data['price_change_percent']} %"))
                    self.ui.tableWidget_2.setItem(
                        row_num, 2, percent_change_item)
                    if data['price_change_percent'] > 0:
                        percent_change_item.setForeground(QColor("green"))
                    elif data['price_change_percent'] < 0:
                        percent_change_item.setForeground(QColor("red"))

                    # Рахуємо PNL
                    now_price = round(sum(list(map(
                        lambda x: x[0] * data['price'], self.database.get_count_purchase_price(str(currency_pair))))), 2)
                    total_balance.append(now_price)
                    purchase_price = sum(
                        item[0] *
                        item[1] for item in self.database.get_count_purchase_price(
                            str(currency_pair)))

                    pnl = QTableWidgetItem(
                        str(f"{round(now_price-purchase_price, 2)} $"))
                    self.ui.tableWidget_2.setItem(row_num, 3, pnl)
                    total_pnl.append(round(now_price - purchase_price, 2))
                    if (now_price - purchase_price) > 0:
                        pnl.setForeground(QColor("green"))
                    elif (now_price - purchase_price) < 0:
                        pnl.setForeground(QColor("red"))
                self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
                self.ui.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            # Виводимо загальний баланс
            self.ui.total_balance.setVisible(True)
            if round(sum(total_balance)) > 0:
                self.ui.total_balance.setText(
                    str(f"<html>Ваш загальний баланс ≈ <font color='green'>{round(sum(total_balance), 2)} $</font></html>"))
            elif round(sum(total_balance)) < 0:
                self.ui.total_balance.setText(
                    str(f"<html>Ваш загальний баланс ≈ <font color='red'>{round(sum(total_balance), 2)} $</font></html>"))
            else:
                self.ui.total_balance.setText(
                    str(f"Ваш загальний баланс ≈ {round(sum(total_balance), 2)} $"))
            # Виводимо загальний PNL
            self.ui.total_pnl.setVisible(True)
            if round(sum(total_pnl), 2) > 0:
                self.ui.total_pnl.setText(
                    str(f"<html>Ваш загальний PNL ≈ <font color='green'>{round(sum(total_pnl), 2)} $</font></html>"))
            elif round(sum(total_pnl), 2) < 0:
                self.ui.total_pnl.setText(
                    str(f"<html>Ваш загальний PNL ≈ <font color='red'>{round(sum(total_pnl), 2)} $</font></html>"))
            else:
                self.ui.total_pnl.setText(
                    str(f"Ваш загальний PNL ≈ {round(sum(total_pnl), 2)} $"))

    def update_button_state(self):
        selected_items = self.ui.tableWidget.selectedItems()
        is_cell_selected = len(selected_items) > 0
        self.ui.deleteDBButton.setEnabled(is_cell_selected)

    def delete_selected_row(self):
        selected_row = self.ui.tableWidget.currentRow()
        if selected_row >= 0 and self.ui.tableWidget.item(
                selected_row, 0) is not None:
            reply = QMessageBox.question(
                self,
                'Підтвердження видалення',
                'Ви впевнені, що хочете видалити обраний рядок?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if reply == QMessageBox.Yes:
                identifier = self.ui.tableWidget.item(selected_row, 0).text()
                with self.database as db:
                    db.delete_coin(identifier)
                self.ui.tableWidget.removeRow(selected_row)
                self.populate_table()

    def return_to_main_window(self):
        self.new_entry_window.close()
        self.show()

    def add_new_row(self):
        name = (self.ui_entry_window.nameEdit.text()).upper()
        count = self.ui_entry_window.countEdit.text()
        price = self.ui_entry_window.PriceEdit.text()
        if name.endswith("USDT"):
            if count and price:
                with self.database as db:
                    db.add_coin_to_db(name, float(count), float(price))
            else:
                with self.database as db:
                    db.add_coin_to_db(name)
            self.populate_table()
            self.new_entry_window.hide()
            self.show()
        else:
            error_box = QMessageBox(
                QMessageBox.Critical,
                "Помилка",
                "Назва повинна закінчуватися на USDT\n Наприклад BTCUSDT",
                QMessageBox.Ok)
            error_box.exec_()

    def populate_table(self):
        with self.database as db:
            cursor = db.cur
            cursor.execute(
                'SELECT name_crypto, sum(count) FROM crypto GROUP BY name_crypto')
            data = cursor.fetchall()
            if len(data) != 0:
                self.ui.refreshButton.setEnabled(True)
                self.ui.tableWidget.setRowCount(len(data))
                self.ui.tableWidget.setColumnCount(len(data[0]))
                self.ui.tableWidget.clear()
                for row_num, row_data in enumerate(data):
                    for col_num, col_data in enumerate(row_data):
                        item = QTableWidgetItem(str(col_data))
                        self.ui.tableWidget.setItem(row_num, col_num, item)
                self.ui.tableWidget.clearFocus()
            else:
                self.ui.refreshButton.setEnabled(False)
        self.ui.tableWidget.itemSelectionChanged.connect(
            self.disable_selection_in_second_column)

    def disable_selection_in_second_column(self):
        selected_items = self.ui.tableWidget.selectedItems()
        for item in selected_items:
            if item.column() == 1:
                self.ui.tableWidget.clearSelection()

    def show_new_entry_window(self):
        self.new_entry_window = QtWidgets.QDialog()  # Створення нового вікна
        self.ui_entry_window = Ui_new_entry_db()  # Інформація про вікно
        self.ui_entry_window.setupUi(self.new_entry_window)  # Застосування інформації з Ui_new_entry_db
        self.hide()
        self.new_entry_window.show()
        self.ui_entry_window.addB.clicked.connect(self.add_new_row)
        self.ui_entry_window.backB.clicked.connect(self.return_to_main_window)

        self.ui_entry_window.nameEdit.textChanged.connect(
            self.check_text_new_entry)
        self.ui_entry_window.countEdit.textChanged.connect(
            self.check_text_new_entry)
        reg_exp = QRegExp("[0-9]+\\.?[0-9]*")
        self.ui_entry_window.PriceEdit.textChanged.connect(
            self.check_text_new_entry)
        validator = QRegExpValidator(reg_exp, self)
        self.ui_entry_window.countEdit.setValidator(validator)

    def check_text_new_entry(self):
        selected_items = 1 if self.ui_entry_window.nameEdit.text() else 0
        is_cell_selected = selected_items > 0
        self.ui_entry_window.addB.setEnabled(is_cell_selected)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])  # Cтворення qt об'єкта
    application = MyWindow()  # Cтворення вікна
    application.show()  # Показуємо вікно
    sys.exit(app.exec_())  # Головний цикл та код виходу
