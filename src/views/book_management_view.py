from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from datetime import datetime

class BookManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, ISBN, or genre...")
        self.search_button = QPushButton("Search")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Author", "ISBN", "Year", "Publisher", "Pages", "Genre"
        ])
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire rows
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)  # Hide vertical header
        
        # Auto-adjust column widths
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, header.Stretch)
            
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(QIcon.fromTheme("list-add"), "Add Book")
        self.edit_button = QPushButton(QIcon.fromTheme("document-edit"), "Edit Book")
        self.delete_button = QPushButton(QIcon.fromTheme("edit-delete"), "Delete Book")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        
        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def show_books(self, books):
        self.table.setRowCount(len(books))
        for row_idx, row in enumerate(books):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_book_dialog(self, book_data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Book" if book_data else "Add Book")
        layout = QFormLayout()
        
        title = QLineEdit(book_data.get('title', '') if book_data else '')
        subtitle = QLineEdit(book_data.get('subtitle', '') if book_data else '')
        author = QLineEdit(book_data.get('author', '') if book_data else '')
        isbn = QLineEdit(book_data.get('isbn', '') if book_data else '')
        scan_button = QPushButton(QIcon.fromTheme("camera-web"), "Scan ISBN")
        publication_year = QSpinBox()
        publication_year.setRange(1000, datetime.now().year + 1)
        publication_year.setValue(book_data.get('publication_year', datetime.now().year) if book_data else datetime.now().year)
        publisher = QLineEdit(book_data.get('publisher', '') if book_data else '')
        pages = QSpinBox()
        pages.setRange(1, 10000)
        pages.setValue(book_data.get('pages', 1) if book_data else 1)
        language = QComboBox()
        language.addItems(['English', 'Spanish', 'French', 'German', 'Other'])
        if book_data and book_data.get('language'):
            language.setCurrentText(book_data['language'])
        genre = QComboBox()
        genre.addItems(['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', 'Other'])
        if book_data and book_data.get('genre'):
            genre.setCurrentText(book_data['genre'])
        description = QLineEdit(book_data.get('description', '') if book_data else '')
        
        layout.addRow("Title:", title)
        layout.addRow("Subtitle:", subtitle)
        layout.addRow("Author:", author)
        isbn_layout = QHBoxLayout()
        isbn_layout.addWidget(isbn)
        isbn_layout.addWidget(scan_button)
        layout.addRow("ISBN:", isbn_layout)
        layout.addRow("Publication Year:", publication_year)
        layout.addRow("Publisher:", publisher)
        layout.addRow("Pages:", pages)
        layout.addRow("Language:", language)
        layout.addRow("Genre:", genre)
        layout.addRow("Description:", description)
        
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        
        return dialog, {
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'isbn': isbn,
            'scan_button': scan_button,
            'publication_year': publication_year,
            'publisher': publisher,
            'pages': pages,
            'language': language,
            'genre': genre,
            'description': description,
            'save_button': save_button,
            'cancel_button': cancel_button
        }