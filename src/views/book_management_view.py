from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QDialog, 
                             QFormLayout, QComboBox, QSpinBox, QLabel, QToolButton, 
                             QDateEdit, QFrame, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime
from icon_manager import icon_manager
import os
from PyQt5.QtCore import QFile, QTextStream

class StyledButton(QPushButton):
    """Custom styled button with hover effects"""
    def __init__(self, text, icon_name=None, primary=False):
        super().__init__(text)
        if icon_name:
            try:
                self.setIcon(icon_manager.get_icon(icon_name))
            except:
                pass  # No icon if manager fails
        self.primary = primary
        self.setProperty("primary", str(primary).lower())

class StyledToolButton(QToolButton):
    """Custom styled tool button"""
    def __init__(self, icon_name, tooltip="", button_type="default"):
        super().__init__()
        self.setIcon(icon_manager.get_icon(icon_name))
        self.setToolTip(tooltip)
        self.setProperty("button_type", button_type)

class SearchFrame(QFrame):
    """Styled search and filter frame"""
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setObjectName("searchFrame")
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(12)

class BookManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.copies_table = None
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        """Load styles from external CSS file"""
        css_file = QFile("assets/css/book_management.css")
        if css_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(css_file)
            self.setStyleSheet(stream.readAll())
            css_file.close()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("📚 Book Management")
        title_label.setObjectName("titleLabel")
        
        # Search and filter frame
        search_frame = SearchFrame()
        
        # Search and filter widgets
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by title, author, ISBN, or genre...")
        self.search_input.setMinimumHeight(40)
        
        self.genre_filter = QComboBox()
        self.genre_filter.addItems(['All', 'Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', 'Other'])
        self.genre_filter.setMinimumHeight(40)
        
        self.year_min = QSpinBox()
        self.year_min.setRange(1000, datetime.now().year + 1)
        self.year_min.setValue(1000)
        self.year_min.setMinimumHeight(40)
        
        self.year_max = QSpinBox()
        self.year_max.setRange(1000, datetime.now().year + 1)
        self.year_max.setValue(datetime.now().year + 1)
        self.year_max.setMinimumHeight(40)
        
        self.search_button = StyledButton("Search", "search", primary=True)
        self.clear_search_button = StyledButton("Clear", "delete")
        
        # Add widgets to search frame layout
        search_frame.layout().addWidget(QLabel("Search:"))
        search_frame.layout().addWidget(self.search_input, 2)
        search_frame.layout().addWidget(QLabel("Genre:"))
        search_frame.layout().addWidget(self.genre_filter)
        search_frame.layout().addWidget(QLabel("Year Range:"))
        search_frame.layout().addWidget(self.year_min)
        search_frame.layout().addWidget(QLabel("-"))
        search_frame.layout().addWidget(self.year_max)
        search_frame.layout().addWidget(self.search_button)
        search_frame.layout().addWidget(self.clear_search_button)
        
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
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        # Column setup
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        
        # Set initial column widths
        column_widths = [60, 200, 150, 120, 80, 120, 80, 100, 80, 140]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        
        # Set resize modes
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Author
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # ISBN
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Year
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Publisher
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Pages
        header.setSectionResizeMode(7, QHeaderView.Interactive)  # Genre
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Copies
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # Actions
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.add_button = StyledButton("➕ Add Book", "add", primary=True)
        self.add_button.setShortcut('Ctrl+A')
        self.add_button.setMinimumHeight(45)
        
        self.edit_button = StyledButton("✏️ Edit Book", "edit")
        self.edit_button.setShortcut('Ctrl+E')
        self.edit_button.setMinimumHeight(45)
        
        self.delete_button = StyledButton("🗑️ Delete Book", "delete")
        self.delete_button.setShortcut('Ctrl+D')
        self.delete_button.setMinimumHeight(45)
        
        self.import_button = StyledButton("📥 Import Books", "import")
        self.import_button.setMinimumHeight(45)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.import_button)
        button_layout.addStretch()
        
        button_frame.setLayout(button_layout)
        
        # Add all components to main layout
        self.layout.addWidget(title_label)
        self.layout.addWidget(search_frame)
        self.layout.addWidget(self.table, 1)
        self.layout.addWidget(button_frame)
        
        self.setLayout(self.layout)

    def resize_columns(self):
        """Enhanced column resizing with better proportions"""
        header = self.table.horizontalHeader()
        
        # Get total available width
        total_width = self.table.viewport().width()
        
        # Reserve space for fixed columns
        fixed_width = 60 + 80 + 80 + 140  # ID + Year + Pages + Copies + Actions
        available_width = total_width - fixed_width
        
        # Distribute remaining width proportionally
        if available_width > 0:
            title_width = int(available_width * 0.3)
            author_width = int(available_width * 0.25)
            isbn_width = int(available_width * 0.15)
            publisher_width = int(available_width * 0.2)
            genre_width = int(available_width * 0.1)
            
            self.table.setColumnWidth(1, max(title_width, 150))
            self.table.setColumnWidth(2, max(author_width, 120))
            self.table.setColumnWidth(3, max(isbn_width, 100))
            self.table.setColumnWidth(5, max(publisher_width, 100))
            self.table.setColumnWidth(7, max(genre_width, 80))

    def show_books(self, books):
        """Enhanced book display with better formatting and styling"""
        self.table.clearContents()
        self.table.setRowCount(len(books))
        current_year = datetime.now().year
        
        for row_idx, row in enumerate(books):
            # Set row height for better appearance
            self.table.setRowHeight(row_idx, 50)
            
            # Display book data with enhanced formatting
            for col_idx, value in enumerate(row[:8]):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Add special formatting for certain columns
                if col_idx == 4:  # Year column
                    year = int(value) if str(value).isdigit() else 0
                    if year > current_year - 5:
                        item.setBackground(QColor("#E8F5E8"))  # Light green for recent books
                elif col_idx == 6:  # Pages column
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                
                self.table.setItem(row_idx, col_idx, item)
            
            # Copy count with enhanced styling
            copy_count = str(row[9]) if len(row) > 9 else "0"
            copy_item = QTableWidgetItem(copy_count)
            copy_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            
            # Color code based on availability
            copies = int(copy_count) if copy_count.isdigit() else 0
            if copies == 0:
                copy_item.setBackground(QColor("#FFEBEE"))  # Light red
                copy_item.setForeground(QColor("#D32F2F"))  # Red text
            elif copies < 3:
                copy_item.setBackground(QColor("#FFF3E0"))  # Light orange
                copy_item.setForeground(QColor("#F57C00"))  # Orange text
            else:
                copy_item.setBackground(QColor("#E8F5E8"))  # Light green
                copy_item.setForeground(QColor("#388E3C"))  # Green text
            
            self.table.setItem(row_idx, 8, copy_item)
            
            # Enhanced action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(4, 4, 4, 4)
            action_layout.setSpacing(4)
            
            book_id = str(row[0])
            edit_btn = StyledToolButton("edit", "Edit Book", "edit")
            edit_btn.setProperty('book_id', book_id)
            
            add_copy_btn = StyledToolButton("add", "Manage Copies", "add")
            add_copy_btn.setProperty('book_id', book_id)
            
            delete_btn = StyledToolButton("delete", "Delete Book", "delete")
            delete_btn.setProperty('book_id', book_id)
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(add_copy_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 9, action_widget)
        
        self.resize_columns()

    def show_error(self, message):
        """Enhanced error dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("❌ Error")
        msg.setText(message)
        msg.setObjectName("errorDialog")
        msg.exec_()

    def show_book_dialog(self, book_data=None):
        """Enhanced book dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📝 Edit Book" if book_data else "➕ Add New Book")
        dialog.setModal(True)
        dialog.resize(500, 600)
        dialog.setObjectName("bookDialog")
        
        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form fields
        title = QLineEdit(book_data.get('title', '') if book_data else '')
        title.setPlaceholderText("Enter book title...")
        
        subtitle = QLineEdit(book_data.get('subtitle', '') if book_data else '')
        subtitle.setPlaceholderText("Enter subtitle (optional)...")
        
        author = QLineEdit(book_data.get('author', '') if book_data else '')
        author.setPlaceholderText("Enter author name...")
        
        isbn = QLineEdit(book_data.get('isbn', '') if book_data else '')
        isbn.setPlaceholderText("Enter ISBN...")
        
        scan_button = StyledButton("📱 Scan ISBN", "scan")
        
        publication_year = QSpinBox()
        publication_year.setRange(1000, datetime.now().year + 1)
        publication_year.setValue(book_data.get('publication_year', datetime.now().year) if book_data else datetime.now().year)
        
        publisher = QLineEdit(book_data.get('publisher', '') if book_data else '')
        publisher.setPlaceholderText("Enter publisher name...")
        
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
        description.setPlaceholderText("Enter book description...")
        
        # Add form rows
        layout.addRow("📖 Title:", title)
        layout.addRow("📄 Subtitle:", subtitle)
        layout.addRow("👤 Author:", author)
        
        isbn_layout = QHBoxLayout()
        isbn_layout.addWidget(isbn, 3)
        isbn_layout.addWidget(scan_button, 1)
        layout.addRow("🔢 ISBN:", isbn_layout)
        
        layout.addRow("📅 Publication Year:", publication_year)
        layout.addRow("🏢 Publisher:", publisher)
        layout.addRow("📜 Pages:", pages)
        layout.addRow("🌍 Language:", language)
        layout.addRow("📚 Genre:", genre)
        layout.addRow("📝 Description:", description)
        
        # Buttons
        save_button = StyledButton("💾 Save Book", primary=True)
        save_button.setMinimumHeight(40)
        
        cancel_button = StyledButton("❌ Cancel")
        cancel_button.setMinimumHeight(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
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
        """Enhanced book copies dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📋 Manage Copies for '{book_title}'")
        dialog.resize(700, 500)
        dialog.setModal(True)
        dialog.setObjectName("copiesDialog")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title with book info
        title_label = QLabel(f"📚 Managing Copies for: {book_title}")
        title_label.setObjectName("titleLabel")
        
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
        self.copies_table.setMinimumHeight(300)
        
        # Column setup
        header = self.copies_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        
        self.copies_table.setColumnWidth(0, 80)
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.add_copy_button = StyledButton("➕ Add Copy", "add", primary=True)
        self.add_copy_button.setMinimumHeight(40)
        
        self.edit_copy_button = StyledButton("✏️ Edit Copy", "edit")
        self.edit_copy_button.setMinimumHeight(40)
        
        self.delete_copy_button = StyledButton("🗑️ Delete Copy", "delete")
        self.delete_copy_button.setMinimumHeight(40)
        
        self.close_copy_button = StyledButton("❌ Close")
        self.close_copy_button.setMinimumHeight(40)
        
        button_layout.addWidget(self.add_copy_button)
        button_layout.addWidget(self.edit_copy_button)
        button_layout.addWidget(self.delete_copy_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_copy_button)
        
        button_frame.setLayout(button_layout)
        
        layout.addWidget(title_label)
        layout.addWidget(self.copies_table, 1)
        layout.addWidget(button_frame)
        dialog.setLayout(layout)
        
        return dialog, {
            'book_id': book_id,
            'add_button': self.add_copy_button,
            'edit_button': self.edit_copy_button,
            'delete_button': self.delete_copy_button,
            'close_button': self.close_copy_button
        }

    def show_book_copy_dialog(self, book_id, copy_data=None):
        """Enhanced book copy dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Edit Copy" if copy_data else "➕ Add New Copy")
        dialog.setModal(True)
        dialog.resize(450, 350)
        dialog.setObjectName("copyDialog")
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Form fields
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
        conditions = ['excellent', 'good', 'fair', 'poor']
        current_condition.addItems(conditions)
        if copy_data and copy_data.get('current_condition'):
            current_condition.setCurrentText(copy_data['current_condition'])
        
        status = QComboBox()
        statuses = ['available', 'loaned', 'reserved', 'lost']
        status.addItems(statuses)
        if copy_data and copy_data.get('status'):
            status.setCurrentText(copy_data['status'])
        
        # Add form rows
        layout.addRow("🏷️ Copy Number:", copy_number)
        layout.addRow("📅 Acquisition Date:", acquisition_date)
        layout.addRow("⭐ Condition:", current_condition)
        layout.addRow("📊 Status:", status)
        
        # Buttons
        save_button = StyledButton("💾 Save Copy", primary=True)
        save_button.setMinimumHeight(40)
        
        cancel_button = StyledButton("❌ Cancel")
        cancel_button.setMinimumHeight(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
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

    def show_copies(self, copies):
        """Display copies in the copies table"""
        if not hasattr(self, 'copies_table'):
            return
            
        self.copies_table.setRowCount(len(copies))
        
        for row_idx, copy in enumerate(copies):
            self.copies_table.setRowHeight(row_idx, 45)
            
            # Copy ID
            id_item = QTableWidgetItem(str(copy[0]))
            id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.copies_table.setItem(row_idx, 0, id_item)
            
            # Copy Number
            number_item = QTableWidgetItem(str(copy[2]))
            number_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.copies_table.setItem(row_idx, 1, number_item)
            
            # Acquisition Date
            date_item = QTableWidgetItem(str(copy[3]))
            date_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.copies_table.setItem(row_idx, 2, date_item)
            
            # Condition with color coding
            condition_item = QTableWidgetItem(str(copy[4]))
            condition_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            condition = str(copy[4]).lower()
            if condition == 'excellent':
                condition_item.setBackground(QColor("#E8F5E8"))
                condition_item.setForeground(QColor("#2E7D32"))
            elif condition == 'good':
                condition_item.setBackground(QColor("#E3F2FD"))
                condition_item.setForeground(QColor("#1565C0"))
            elif condition == 'fair':
                condition_item.setBackground(QColor("#FFF3E0"))
                condition_item.setForeground(QColor("#EF6C00"))
            else:  # poor
                condition_item.setBackground(QColor("#FFEBEE"))
                condition_item.setForeground(QColor("#C62828"))
            self.copies_table.setItem(row_idx, 3, condition_item)
            
            # Status with color coding
            status_item = QTableWidgetItem(str(copy[5]))
            status_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            status = str(copy[5]).lower()
            if status == 'available':
                status_item.setBackground(QColor("#E8F5E8"))
                status_item.setForeground(QColor("#2E7D32"))
            elif status == 'loaned':
                status_item.setBackground(QColor("#FFF3E0"))
                status_item.setForeground(QColor("#EF6C00"))
            elif status == 'reserved':
                status_item.setBackground(QColor("#E3F2FD"))
                status_item.setForeground(QColor("#1565C0"))
            else:  # lost
                status_item.setBackground(QColor("#FFEBEE"))
                status_item.setForeground(QColor("#C62828"))
            self.copies_table.setItem(row_idx, 4, status_item)