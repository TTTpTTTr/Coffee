import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.pushButton.clicked.connect(self.load_data)
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
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        self.tableWidget.horizontalHeader().setStretchLastSection(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
