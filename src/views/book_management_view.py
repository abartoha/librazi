from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QLabel, QToolButton, QDateEdit
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QColor
from datetime import datetime

class BookManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # Search and filter bar
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, ISBN, or genre...")
        self.search_button = QPushButton("Search")
        self.clear_search_button = QPushButton("Clear")
        self.genre_filter = QComboBox()
        self.genre_filter.addItems(['All', 'Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', 'Other'])
        self.year_min = QSpinBox()
        self.year_min.setRange(1000, datetime.now().year + 1)
        self.year_min.setValue(1000)
        self.year_max = QSpinBox()
        self.year_max.setRange(1000, datetime.now().year + 1)
        self.year_max.setValue(datetime.now().year + 1)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("Genre:"))
        filter_layout.addWidget(self.genre_filter)
        filter_layout.addWidget(QLabel("Year Range:"))
        filter_layout.addWidget(self.year_min)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.year_max)
        filter_layout.addWidget(self.search_button)
        filter_layout.addWidget(self.clear_search_button)
        
        # Book Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Author", "ISBN", "Year", "Publisher", "Pages", "Genre", "Copies", "Actions"
        ])
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        
        # Initial column setup
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount() - 2):
            header.setSectionResizeMode(i, header.Stretch)
        header.setSectionResizeMode(8, header.Fixed)
        header.setSectionResizeMode(9, header.Fixed)
        self.table.setColumnWidth(8, 60)
        self.table.setColumnWidth(9, 120)
            
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(QIcon("assets/icon/add.png"), "Add Book")
        self.add_button.setShortcut('Ctrl+A')
        self.edit_button = QPushButton(QIcon("assets/icon/edit.png"), "Edit Book")
        self.edit_button.setShortcut('Ctrl+E')
        self.delete_button = QPushButton(QIcon("assets/icon/delete.png"), "Delete Book")
        self.delete_button.setShortcut('Ctrl+D')
        self.import_button = QPushButton(QIcon("assets/icon/import.png"), "Import Books")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.import_button)
        
        self.layout.addLayout(filter_layout)
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def resize_columns(self):
        header = self.table.horizontalHeader()
        # Resize all columns based on content
        self.table.resizeColumnsToContents()
        # Enforce minimum and maximum widths for better readability
        for i in range(self.table.columnCount()):
            current_width = self.table.columnWidth(i)
            if i == 8:  # Copies column
                self.table.setColumnWidth(i, max(60, min(current_width, 80)))
            elif i == 9:  # Actions column
                self.table.setColumnWidth(i, 120)
            else:
                # Ensure other columns are between 100 and 300 pixels
                self.table.setColumnWidth(i, max(100, min(current_width, 300)))
        # Restore stretch for non-fixed columns
        for i in range(self.table.columnCount() - 2):
            header.setSectionResizeMode(i, header.Stretch)

    def show_books(self, books):
        self.table.setRowCount(len(books))
        current_year = datetime.now().year
        for row_idx, row in enumerate(books):
            for col_idx, value in enumerate(row[:8]):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
            
            # Copy count
            copy_count = str(row[9])
            copy_item = QTableWidgetItem(copy_count)
            copy_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.table.setItem(row_idx, 8, copy_item)
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(2)
            
            edit_btn = QToolButton()
            edit_btn.setIcon(QIcon("assets/icon/edit.png"))
            edit_btn.setProperty('row', row_idx)
            edit_btn.setToolTip("Edit Book")
            
            delete_btn = QToolButton()
            delete_btn.setIcon(QIcon("assets/icon/delete.png"))
            delete_btn.setProperty('row', row_idx)
            delete_btn.setToolTip("Delete Book")
            
            add_copy_btn = QToolButton()
            add_copy_btn.setIcon(QIcon("assets/icon/add.png"))
            add_copy_btn.setProperty('row', row_idx)
            add_copy_btn.setToolTip("Manage Book Copies")
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(add_copy_btn)
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 9, action_widget)
            
        self.resize_columns()

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
        scan_button = QPushButton(QIcon("assets/icon/scan.png"), "Scan ISBN")
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

    def show_book_copies_dialog(self, book_id, book_title):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Manage Copies for '{book_title}'")
        dialog.resize(600, 400)
        layout = QVBoxLayout()
        
        # Copies Table
        self.copies_table = QTableWidget()
        self.copies_table.setColumnCount(5)
        self.copies_table.setHorizontalHeaderLabels([
            "Copy ID", "Copy Number", "Acquisition Date", "Condition", "Status"
        ])
        self.copies_table.setSelectionMode(QTableWidget.SingleSelection)
        self.copies_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.copies_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.copies_table.setAlternatingRowColors(True)
        self.copies_table.verticalHeader().setVisible(False)
        
        header = self.copies_table.horizontalHeader()
        for i in range(self.copies_table.columnCount()):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_copy_button = QPushButton(QIcon("assets/icon/add.png"), "Add Copy")
        self.edit_copy_button = QPushButton(QIcon("assets/icon/edit.png"), "Edit Copy")
        self.delete_copy_button = QPushButton(QIcon("assets/icon/delete.png"), "Delete Copy")
        self.close_copy_button = QPushButton("Close")
        button_layout.addWidget(self.add_copy_button)
        button_layout.addWidget(self.edit_copy_button)
        button_layout.addWidget(self.delete_copy_button)
        button_layout.addWidget(self.close_copy_button)
        
        layout.addWidget(self.copies_table)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        return dialog, {
            'book_id': book_id,
            'add_button': self.add_copy_button,
            'edit_button': self.edit_copy_button,
            'delete_button': self.delete_copy_button,
            'close_button': self.close_copy_button
        }

    def show_book_copy_dialog(self, book_id, copy_data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Copy" if copy_data else "Add Copy")
        layout = QFormLayout()
        
        copy_number = QLineEdit(copy_data.get('copy_number', '') if copy_data else '')
        copy_number.setPlaceholderText(f"e.g., {book_id}-COPY-001")
        acquisition_date = QDateEdit()
        acquisition_date.setCalendarPopup(True)
        acquisition_date.setMaximumDate(QDate.currentDate())
        acquisition_date.setDate(
            copy_data.get('acquisition_date', QDate.currentDate()) 
            if copy_data and copy_data.get('acquisition_date') 
            else QDate.currentDate()
        )
        current_condition = QComboBox()
        current_condition.addItems(['excellent', 'good', 'fair', 'poor'])
        if copy_data and copy_data.get('current_condition'):
            current_condition.setCurrentText(copy_data['current_condition'])
        status = QComboBox()
        status.addItems(['available', 'loaned', 'reserved', 'lost'])
        if copy_data and copy_data.get('status'):
            status.setCurrentText(copy_data['status'])
        
        layout.addRow("Copy Number:", copy_number)
        layout.addRow("Acquisition Date:", acquisition_date)
        layout.addRow("Condition:", current_condition)
        layout.addRow("Status:", status)
        
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        
        dialog.setLayout(layout)
        
        return dialog, {
            'copy_number': copy_number,
            'acquisition_date': acquisition_date,
            'current_condition': current_condition,
            'status': status,
            'save_button': save_button,
            'cancel_button': cancel_button
        }