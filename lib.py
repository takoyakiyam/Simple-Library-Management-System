import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QTabWidget, 
                             QDateEdit, QInputDialog, QAbstractItemView, QHeaderView)
from PyQt5.QtCore import QDate
import pandas as pd

BOOK_FILE = 'books.txt'

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Library Management System - Welcome')
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout()

        # Welcome Label
        self.welcome_label = QLabel("Welcome to Library Management System")
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        self.layout.addWidget(self.welcome_label)

        # Open Button
        self.open_button = QPushButton("Open Library System")
        self.open_button.clicked.connect(self.open_library_system)
        self.layout.addWidget(self.open_button)

        self.setLayout(self.layout)

    def open_library_system(self):
        self.library_window = LibraryManagementSystem()
        self.library_window.show()
        self.close()


class LibraryManagementSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Library Management System')
        self.setGeometry(100, 100, 800, 600)

        # Layout and Tabs
        self.tabs = QTabWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tabs)

        self.book_tab = QWidget()
        self.borrowed_tab = QWidget()

        self.tabs.addTab(self.book_tab, "Books")
        self.tabs.addTab(self.borrowed_tab, "Borrowed Books")

        # Initialize tabs
        self.init_books_tab()
        self.init_borrowed_tab()

        self.setLayout(self.main_layout)

        # Data storage
        self.book_data = pd.DataFrame(columns=['Title', 'Author', 'Year'])
        self.borrowed_books = pd.DataFrame(columns=['Borrower', 'Title', 'Borrow Date', 'Return Date'])

        # Load books from file
        self.load_books_from_file()

    def init_books_tab(self):
        layout = QVBoxLayout()

        # Book Entry Fields
        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()

        self.author_label = QLabel("Author:")
        self.author_input = QLineEdit()

        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit()

        self.add_book_button = QPushButton("Add Book")
        self.add_book_button.clicked.connect(self.add_book)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Title")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_book)

        # Book List Table
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(3)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.book_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.book_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.book_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.book_table.setHorizontalHeaderLabels(["Title", "Author", "Year"])

        # Borrow Book Button
        self.borrow_book_button = QPushButton("Borrow Selected Book")
        self.borrow_book_button.clicked.connect(self.borrow_book)

        # Remove Book Button
        self.remove_book_button = QPushButton("Remove Selected Book")
        self.remove_book_button.clicked.connect(self.remove_book)

        # Layout for buttons and search
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_input)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.borrow_book_button)
        button_layout.addWidget(self.remove_book_button)

        # Adding widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_input)
        layout.addWidget(self.add_book_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.book_table)

        self.book_tab.setLayout(layout)

    def init_borrowed_tab(self):
        layout = QVBoxLayout()

        self.borrowed_table = QTableWidget()
        self.borrowed_table.setColumnCount(4)
        self.borrowed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.borrowed_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.borrowed_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.borrowed_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.borrowed_table.setHorizontalHeaderLabels(["Borrower", "Title", "Borrow Date", "Return Date"])

        layout.addWidget(self.borrowed_table)
        self.borrowed_tab.setLayout(layout)

    def load_books_from_file(self):
        try:
            with open(BOOK_FILE, 'r') as f:
                lines = f.readlines()

            # Populate DataFrame with file data
            for line in lines:
                title, author, year = line.strip().split(',')
                new_book = pd.DataFrame([[title, author, year]], columns=['Title', 'Author', 'Year'])
                self.book_data = pd.concat([self.book_data, new_book], ignore_index=True)

            self.update_book_table()

        except FileNotFoundError:
            QMessageBox.information(self, "File Error", "No book file found. Starting fresh.")

    def add_book(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()

        if title and author and year:
            # Add book to the data storage
            new_book = pd.DataFrame([[title, author, year]], columns=['Title', 'Author', 'Year'])
            self.book_data = pd.concat([self.book_data, new_book], ignore_index=True)

            # Save to the .txt file
            with open(BOOK_FILE, 'a') as f:
                f.write(f'{title},{author},{year}\n')

            # Update UI Table
            self.update_book_table()

            # Clear input fields
            self.title_input.clear()
            self.author_input.clear()
            self.year_input.clear()

        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")

    def update_book_table(self):
        self.book_table.setRowCount(len(self.book_data))
        for row in range(len(self.book_data)):
            self.book_table.setItem(row, 0, QTableWidgetItem(self.book_data.iloc[row]['Title']))
            self.book_table.setItem(row, 1, QTableWidgetItem(self.book_data.iloc[row]['Author']))
            self.book_table.setItem(row, 2, QTableWidgetItem(self.book_data.iloc[row]['Year']))

    def remove_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            # Remove the selected row from the data and table
            title_to_remove = self.book_data.iloc[selected_row]['Title']
            self.book_data = self.book_data.drop(selected_row).reset_index(drop=True)
            self.update_book_table()

            # Remove from the .txt file
            self.save_books_to_file()

            QMessageBox.information(self, "Success", "Book removed successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a book to remove")

    def save_books_to_file(self):
        with open(BOOK_FILE, 'w') as f:
            for index, row in self.book_data.iterrows():
                f.write(f"{row['Title']},{row['Author']},{row['Year']}\n")

    def search_book(self):
        search_query = self.search_input.text().lower()
        if search_query:
            filtered_books = self.book_data[self.book_data['Title'].str.lower().str.contains(search_query)]

            if not filtered_books.empty:
                self.book_table.setRowCount(len(filtered_books))
                for row in range(len(filtered_books)):
                    self.book_table.setItem(row, 0, QTableWidgetItem(filtered_books.iloc[row]['Title']))
                    self.book_table.setItem(row, 1, QTableWidgetItem(filtered_books.iloc[row]['Author']))
                    self.book_table.setItem(row, 2, QTableWidgetItem(filtered_books.iloc[row]['Year']))
            else:
                QMessageBox.information(self, "No Results", "No books found matching the search query")
        else:
            self.update_book_table()

    def borrow_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            borrower, ok = QInputDialog.getText(self, "Borrow Book", "Enter Borrower's Name:")
            if ok and borrower:
                # Record borrow details
                title = self.book_data.iloc[selected_row]['Title']
                borrow_date = QDate.currentDate().toString("yyyy-MM-dd")
                return_date = QDate.currentDate().addDays(14).toString("yyyy-MM-dd")  # Set return date after 14 days

                borrowed_book = pd.DataFrame([[borrower, title, borrow_date, return_date]],
                                             columns=['Borrower', 'Title', 'Borrow Date', 'Return Date'])
                self.borrowed_books = pd.concat([self.borrowed_books, borrowed_book], ignore_index=True)

                # Update borrowed books table
                self.update_borrowed_table()

                QMessageBox.information(self, "Success", f"{title} has been borrowed by {borrower}!")

    def update_borrowed_table(self):
        self.borrowed_table.setRowCount(len(self.borrowed_books))
        for row in range(len(self.borrowed_books)):
            self.borrowed_table.setItem(row, 0, QTableWidgetItem(self.borrowed_books.iloc[row]['Borrower']))
            self.borrowed_table.setItem(row, 1, QTableWidgetItem(self.borrowed_books.iloc[row]['Title']))
            self.borrowed_table.setItem(row, 2, QTableWidgetItem(self.borrowed_books.iloc[row]['Borrow Date']))
            self.borrowed_table.setItem(row, 3, QTableWidgetItem(self.borrowed_books.iloc[row]['Return Date']))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    welcome.show()
    sys.exit(app.exec_())
