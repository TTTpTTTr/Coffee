import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QAbstractItemView


class AddEditCoffeeForm(QDialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        uic.loadUi("addEditCoffeeForm.ui", self)

        self.coffee_id = coffee_id
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        if self.coffee_id is not None:
            self.load_coffee_data()
            self.setWindowTitle("Изменить запись о кофе")
        else:
            self.setWindowTitle("Добавить запись о кофе")

    def load_coffee_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coffee WHERE id = ?', (self.coffee_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            self.nameEdit.setText(row[1])

            idx = self.roastComboBox.findText(row[2])
            if idx >= 0:
                self.roastComboBox.setCurrentIndex(idx)

            idx = self.formComboBox.findText(row[3])
            if idx >= 0:
                self.formComboBox.setCurrentIndex(idx)

            self.tasteEdit.setText(row[4])
            self.priceSpinBox.setValue(float(row[5]))
            self.volumeEdit.setText(row[6])

    def get_data(self):
        return {
            'name': self.nameEdit.text().strip(),
            'roast_level': self.roastComboBox.currentText(),
            'form': self.formComboBox.currentText(),
            'taste': self.tasteEdit.toPlainText().strip(),
            'price': self.priceSpinBox.value(),
            'volume': self.volumeEdit.text().strip()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.pushButton.clicked.connect(self.load_data)
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

        self.tableWidget.cellDoubleClicked.connect(self.edit_coffee)

        self.load_data()

    def load_data(self):
        self.tableWidget.setRowCount(0)

        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM coffee')
        data = cursor.fetchall()
        conn.close()

        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            'ID', 'Название сорта', 'Степень обжарки',
            'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем'
        ])

        for row_idx, row_data in enumerate(data):
            self.tableWidget.insertRow(row_idx)
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Ошибка", "Название сорта не может быть пустым!")
                return

            conn = sqlite3.connect('coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO coffee (name, roast_level, form, taste, price, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['name'], data['roast_level'], data['form'], data['taste'], data['price'], data['volume']))
            conn.commit()
            conn.close()
            self.load_data()

    def edit_coffee(self):
        selected_rows = self.tableWidget.selectionModel().selectedRows()

        if len(selected_rows) == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return
        elif len(selected_rows) > 1:
            QMessageBox.warning(self, "Ошибка",
                                "Можно редактировать только одну запись за раз! Выберите только одну строку.")
            return

        current_row = self.tableWidget.currentRow()
        coffee_id = int(self.tableWidget.item(current_row, 0).text())

        dialog = AddEditCoffeeForm(self, coffee_id=coffee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Ошибка", "Название сорта не может быть пустым!")
                return

            conn = sqlite3.connect('coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE coffee 
                SET name=?, roast_level=?, form=?, taste=?, price=?, volume=?
                WHERE id=?''',
                           (data['name'], data['roast_level'], data['form'], data['taste'], data['price'],
                            data['volume'], coffee_id))
            conn.commit()
            conn.close()
            self.load_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
