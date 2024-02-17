import pytest
from PyQt5 import QtWidgets

import main


@pytest.fixture
def app(qtbot):
    test_app = main.MyWindow()
    qtbot.addWidget(test_app)
    return test_app


def test_return_to_main_window(app):
    app.show_new_entry_window()    # Показуємо вікно нового запису
    app.new_entry_window.close()    # Закриваємо вікно new_entry_window
    assert not app.isVisible()    # Перевіряємо, що головне вікно програми  показано


def test_show_new_entry_window(app):
    app.show_new_entry_window()  # Виклик методу show_new_entry_window
    # Проверяем, что главное окно действительно скрыто
    assert not app.isVisible()  # Перевірка що головне вікно приховано
    # Проверяем, что окно новой записи отображается
    # Перевірка, що вікно нового запису відображається
    assert app.new_entry_window.isVisible()


def test_check_text_new_entry(app):
    # Додаємо QLineEdit та кнопку QPushButton до вікна
    line_edit = QtWidgets.QLineEdit()
    button = QtWidgets.QPushButton()
    # Підключаємо метод check_text_new_entry до кнопки
    button.clicked.connect(app.check_text_new_entry)
    # Встановлюємо QLineEdit та кнопку до вікна
    app.ui_entry_window = QtWidgets.QDialog()
    app.ui_entry_window.nameEdit = line_edit
    app.ui_entry_window.addB = button
    # Симулюємо введення тексту у QLineEdit та викликаємо метод
    # check_text_new_entry
    line_edit.setText("Some text")
    app.check_text_new_entry()
    # Перевіряємо, що кнопка ввімкнена
    assert button.isEnabled()
    # Очищаємо віджет
    app.close()
