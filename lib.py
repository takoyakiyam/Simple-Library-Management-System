import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QTabWidget, 
                             QTextEdit, QInputDialog, QAbstractItemView, QHeaderView, QDialog, QFormLayout, 
                             QTextBrowser)
from PyQt5.QtCore import QDate
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

nltk.download('vader_lexicon')

BOOK_FILE = 'books.txt'
BORROWER_FILE = 'borrowers.txt'
REVIEW_FILE = 'reviews.txt'

class ReviewDialog(QDialog):
    def __init__(self, book_title, parent=None):
        super().__init__(parent)
        self.book_title = book_title
        self.setWindowTitle(f"Reviews for {book_title}")
        self.layout = QVBoxLayout()

        # Text area to show reviews
        self.review_text = QTextBrowser()
        self.layout.addWidget(self.review_text)

        # Add "Add Review" button
        self.add_review_button = QPushButton("Add a Review")
        self.add_review_button.clicked.connect(self.add_review)
        self.layout.addWidget(self.add_review_button)
        
        # Load and display reviews with sentiment
        self.load_reviews_with_sentiment(book_title)

        self.setLayout(self.layout)

    def load_reviews_with_sentiment(self, book_title):
        reviews = []
        sia = SentimentIntensityAnalyzer()  # VADER sentiment analyzer
        try:
            with open(REVIEW_FILE, 'r') as file:
                for line in file:
                    title, review = map(str.strip, line.strip().split(':', 1))
                    if title.lower() == book_title.lower():
                        # Analyze sentiment of the review using VADER
                        sentiment_scores = sia.polarity_scores(review)
                        sentiment = self.get_sentiment_label(sentiment_scores['compound'])

                        # Append review with sentiment
                        sentiment_color = self.get_sentiment_color(sentiment)
                        reviews.append(f"Review: {review}<br>Sentiment: <span style='font-weight: bold; color: {sentiment_color}'>{sentiment}</span><br><br>")
        except FileNotFoundError:
            reviews = ["No reviews available."]
        
        if reviews:
            self.review_text.setHtml("<br>".join(reviews))
        else:
            self.review_text.setHtml("No reviews available.")

    def get_sentiment_label(self, compound_score):
        """Helper method to classify sentiment based on VADER's compound score."""
        if compound_score >= 0.05:
            return "Positive"
        elif compound_score <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    def get_sentiment_color(self, sentiment):
        """Helper method to get sentiment color."""
        if sentiment == "Positive":
            return "green"
        elif sentiment == "Neutral":
            return "gray"
        else:
            return "red"
    
    def add_review(self):
        # Create a dialog with a QTextEdit for the review
        review_dialog = QDialog(self)
        review_dialog.setWindowTitle("Add a Review")
        layout = QVBoxLayout()
        review_dialog.setLayout(layout)

        # Create a QTextEdit for the review
        self.review_input = QTextEdit()
        self.review_input.setPlaceholderText("Enter your review...")
        layout.addWidget(self.review_input)

        # Create buttons for submitting and canceling the review
        button_layout = QHBoxLayout()
        submit_button = QPushButton("Submit Review")
        submit_button.clicked.connect(review_dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(review_dialog.reject)
        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Show the dialog and get the review
        if review_dialog.exec_() == QDialog.Accepted:
            review = self.review_input.toPlainText()
            if review:
                # Save the review to the file
                with open(REVIEW_FILE, 'a') as file:
                    file.write(f"{self.book_title}:{review}\n")
                
                # Reload the reviews with the new entry
                self.load_reviews_with_sentiment(self.book_title)
            else:
                QMessageBox.warning(self, "Input Error", "Review cannot be empty.")

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Book')
        self.layout = QFormLayout()

        # Book Entry Fields in the dialog
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()

        self.layout.addRow('Title:', self.title_input)
        self.layout.addRow('Author:', self.author_input)
        self.layout.addRow('Year:', self.year_input)

        # Add buttons
        self.add_button = QPushButton('Add Book')
        self.cancel_button = QPushButton('Cancel')

        self.add_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addRow(button_layout)
        self.setLayout(self.layout)

    def get_book_details(self):
        return self.title_input.text(), self.author_input.text(), self.year_input.text()
    
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
        self.load_borrowers_from_file()

    def init_books_tab(self):
        layout = QVBoxLayout()

        # Add Book Button
        self.add_book_button = QPushButton("Add Book")
        self.add_book_button.clicked.connect(self.show_add_book_dialog)

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
        
        # Reviews Button
        self.reviews_button = QPushButton("Show Reviews")
        self.reviews_button.clicked.connect(self.show_reviews)

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
        button_layout.addWidget(self.reviews_button) 
        button_layout.addWidget(self.borrow_book_button)
        button_layout.addWidget(self.remove_book_button)

        # Adding widgets to layout
        layout.addWidget(self.add_book_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.book_table)

        self.book_tab.setLayout(layout)
        
    def show_reviews(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            # Fetch the title from the table instead of directly from book_data to handle filtered data
            book_title = self.book_table.item(selected_row, 0).text()
            dialog = ReviewDialog(book_title, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a book to see its reviews")

    def init_borrowed_tab(self):
        layout = QVBoxLayout()

        self.borrowed_table = QTableWidget()
        self.borrowed_table.setColumnCount(6)
        self.borrowed_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.borrowed_table.setHorizontalHeaderLabels(['Borrower', 'Title', 'Author', 'Year', 'Borrow Date', 'Return Date'])
        self.borrowed_table.horizontalHeader().setStretchLastSection(True)
        
        # Return Book Button
        self.return_book_button = QPushButton("Return Selected Book")
        self.return_book_button.clicked.connect(self.return_book)
    
        layout.addWidget(self.borrowed_table)
        layout.addWidget(self.return_book_button)
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
            
    def show_add_book_dialog(self):
        dialog = AddBookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, author, year = dialog.get_book_details()
            self.add_book(title, author, year)

    def add_book(self, title, author, year):
            if title and author and year:
                # Add book to the data storage
                new_book = pd.DataFrame([[title, author, year]], columns=['Title', 'Author', 'Year'])
                self.book_data = pd.concat([self.book_data, new_book], ignore_index=True)

                # Save to the .txt file
                with open(BOOK_FILE, 'a') as f:
                    f.write(f'\n{title},{author},{year}')

                # Update UI Table
                self.update_book_table()

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

    def save_borrowers_to_file(self):
        with open(BORROWER_FILE, 'w') as f:
            for index, row in self.borrowed_books.iterrows():
                f.write(f"{row['Borrower']},{row['Title']},{row['Author']},{row['Year']},{row['Borrow Date']},{row['Return Date']}\n")
                
    def load_borrowers_from_file(self):
        try:
            with open(BORROWER_FILE, 'r') as f:
                lines = f.readlines()

            # Populate DataFrame with file data
            for line in lines:
                if line.strip(): 
                    borrower, title, author, year, borrow_date, return_date = line.strip().split(',')
                    new_borrow = pd.DataFrame([[borrower, title, author, year, borrow_date, return_date]],
                                            columns=['Borrower', 'Title', 'Author', 'Year', 'Borrow Date', 'Return Date'])
                    self.borrowed_books = pd.concat([self.borrowed_books, new_borrow], ignore_index=True)

            self.update_borrowed_table()

        except FileNotFoundError:
            QMessageBox.information(self, "File Error", "No borrower file found. Starting fresh.")
        
    def search_book(self):
        search_query = self.search_input.text().lower()
        if search_query:
            # Filter the book data based on the search query
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
            # If no search query, show the entire book list
            self.update_book_table()

    def borrow_book(self):
        selected_row = self.book_table.currentRow()
        if selected_row >= 0:
            borrower, ok = QInputDialog.getText(self, "Borrow Book", "Enter Borrower's Name:")
            if ok and borrower:
                # Get book details
                title = self.book_data.iloc[selected_row]['Title']
                author = self.book_data.iloc[selected_row]['Author']
                year = self.book_data.iloc[selected_row]['Year']
                borrow_date = QDate.currentDate().toString("yyyy-MM-dd")
                return_date = QDate.currentDate().addDays(14).toString("yyyy-MM-dd")  # Set return date after 14 days

                # Add the book to the borrowed books data
                borrowed_book = pd.DataFrame([[borrower, title, author, year, borrow_date, return_date]],
                                            columns=['Borrower', 'Title', 'Author', 'Year', 'Borrow Date', 'Return Date'])
                self.borrowed_books = pd.concat([self.borrowed_books, borrowed_book], ignore_index=True)

                # Remove from available books
                self.book_data = self.book_data.drop(selected_row).reset_index(drop=True)
                self.update_book_table()

                # Save to the borrowers.txt file
                self.save_borrowers_to_file()

                # Save to the books.txt file (after removing the borrowed book)
                self.save_books_to_file()

                # Update borrowed books table
                self.update_borrowed_table()

                QMessageBox.information(self, "Success", f"{title} has been borrowed by {borrower}!")
            else:
                QMessageBox.warning(self, "Input Error", "Borrower's name is required.")

    def save_borrowers_to_file(self):
        with open(BORROWER_FILE, 'w') as f:
            for index, row in self.borrowed_books.iterrows():
                f.write(f"{row['Borrower']},{row['Title']},{row['Author']},{row['Year']},{row['Borrow Date']},{row['Return Date']}\n")
                
    def return_book(self):
        selected_row = self.borrowed_table.currentRow()
        if selected_row >= 0:
            # Get the book details from the borrowed_books DataFrame
            borrower = self.borrowed_books.iloc[selected_row]['Borrower']
            title = self.borrowed_books.iloc[selected_row]['Title']
            author = self.borrowed_books.iloc[selected_row]['Author']  # Author detail
            year = self.borrowed_books.iloc[selected_row]['Year']      # Year detail

            # Add the book back to the available books
            returned_book = pd.DataFrame([[title, author, year]], columns=['Title', 'Author', 'Year'])
            self.book_data = pd.concat([self.book_data, returned_book], ignore_index=True)
            self.update_book_table()

            # Remove from borrowed books
            self.borrowed_books = self.borrowed_books.drop(selected_row).reset_index(drop=True)
            self.update_borrowed_table()

            # Save changes to the borrowers.txt file
            self.save_borrowers_to_file()

            QMessageBox.information(self, "Success", f"{title} has been returned by {borrower}!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a borrowed book to return.")

    def update_borrowed_table(self):
        self.borrowed_table.setRowCount(0)  # Clear the table first
        for index, row in self.borrowed_books.iterrows():
            self.borrowed_table.insertRow(index)
            self.borrowed_table.setItem(index, 0, QTableWidgetItem(str(row['Borrower'])))
            self.borrowed_table.setItem(index, 1, QTableWidgetItem(str(row['Title'])))
            self.borrowed_table.setItem(index, 2, QTableWidgetItem(str(row['Author'])))  # Author column
            self.borrowed_table.setItem(index, 3, QTableWidgetItem(str(row['Year'])))    # Year column
            self.borrowed_table.setItem(index, 4, QTableWidgetItem(str(row['Borrow Date'])))
            self.borrowed_table.setItem(index, 5, QTableWidgetItem(str(row['Return Date'])))
        self.borrowed_table.resizeColumnsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    welcome.show()
    sys.exit(app.exec_())
