import sys
import os
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QAbstractItemView
from ui_main import Ui_MainWindow
from ui_add_edit_coffee import Ui_AddEditCoffeeForm

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, 'data', 'coffee.sqlite')


class AddEditCoffeeForm(QDialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.ui = Ui_AddEditCoffeeForm()
        self.ui.setupUi(self)  # Применяем интерфейс

        self.coffee_id = coffee_id
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

        if self.coffee_id is not None:
            self.load_coffee_data()
            self.setWindowTitle("Изменить запись о кофе")
        else:
            self.setWindowTitle("Добавить запись о кофе")

    def load_coffee_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coffee WHERE id = ?', (self.coffee_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            self.ui.nameEdit.setText(row[1])
            idx = self.ui.roastComboBox.findText(row[2])
            if idx >= 0: self.ui.roastComboBox.setCurrentIndex(idx)
            idx = self.ui.formComboBox.findText(row[3])
            if idx >= 0: self.ui.formComboBox.setCurrentIndex(idx)

            self.ui.tasteEdit.setText(row[4])
            self.ui.priceSpinBox.setValue(float(row[5]))
            self.ui.volumeEdit.setText(row[6])

    def get_data(self):
        return {
            'name': self.ui.nameEdit.text().strip(),
            'roast_level': self.ui.roastComboBox.currentText(),
            'form': self.ui.formComboBox.currentText(),
            'taste': self.ui.tasteEdit.toPlainText().strip(),
            'price': self.ui.priceSpinBox.value(),
            'volume': self.ui.volumeEdit.text().strip()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Применяем интерфейс

        # Настройка поведения таблицы
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.ui.pushButton.clicked.connect(self.load_data)
        self.ui.addButton.clicked.connect(self.add_coffee)
        self.ui.editButton.clicked.connect(self.edit_coffee)
        self.ui.tableWidget.cellDoubleClicked.connect(self.edit_coffee)

        self.load_data()

    def load_data(self):
        self.ui.tableWidget.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coffee')
        data = cursor.fetchall()
        conn.close()

        self.ui.tableWidget.setColumnCount(7)
        self.ui.tableWidget.setHorizontalHeaderLabels([
            'ID', 'Название сорта', 'Степень обжарки',
            'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем'
        ])

        for row_idx, row_data in enumerate(data):
            self.ui.tableWidget.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Ошибка", "Название сорта не может быть пустым!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO coffee (name, roast_level, form, taste, price, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['name'], data['roast_level'], data['form'], data['taste'], data['price'], data['volume']))
            conn.commit()
            conn.close()
            self.load_data()

    def edit_coffee(self):
        selected_rows = self.ui.tableWidget.selectionModel().selectedRows()
        if len(selected_rows) == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return
        elif len(selected_rows) > 1:
            QMessageBox.warning(self, "Ошибка", "Можно редактировать только одну запись за раз!")
            return

        current_row = self.ui.tableWidget.currentRow()
        coffee_id = int(self.ui.tableWidget.item(current_row, 0).text())

        dialog = AddEditCoffeeForm(self, coffee_id=coffee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Ошибка", "Название сорта не может быть пустым!")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE coffee 
                SET name=?, roast_level=?, form=?, taste=?, price=?, volume=?
                WHERE id=?
            ''', (data['name'], data['roast_level'], data['form'], data['taste'], data['price'], data['volume'],
                  coffee_id))
            conn.commit()
            conn.close()
            self.load_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
