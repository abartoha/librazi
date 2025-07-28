from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QToolButton
import csv
import logging
from datetime import datetime

logging.basicConfig(filename='book_management.log', level=logging.ERROR)

class BookController(QObject):
    search_triggered = pyqtSignal(str)
    
    def __init__(self, model, view, copy_controller):
        super().__init__()
        self.model = model
        self.view = view
        self.copy_controller = copy_controller
        self.current_sort_column = 'title'
        self.current_sort_order = 'ASC'
        self.connect_signals()
        self.load_books()

    def connect_signals(self):
        self.view.add_button.clicked.connect(self.show_add_book_dialog)
        self.view.edit_button.clicked.connect(self.show_edit_book_dialog)
        self.view.delete_button.clicked.connect(self.delete_book)
        self.view.search_button.clicked.connect(self.search_books)
        self.view.search_input.returnPressed.connect(self.search_books)
        self.view.clear_search_button.clicked.connect(self.clear_search)
        self.view.import_button.clicked.connect(self.import_books)
        self.view.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.view.table.doubleClicked.connect(self.show_edit_book_dialog)


    def load_books(self, search_query=None, genre=None, year_min=None, year_max=None):
        try:
            books = self.model.get_books(search_query, genre, year_min, year_max, self.current_sort_column, self.current_sort_order)
            self.view.show_books(books)
            for row in range(self.view.table.rowCount()):
                widget = self.view.table.cellWidget(row, 9)
                if widget:
                    edit_btn = widget.layout().itemAt(0).widget()
                    delete_btn = widget.layout().itemAt(1).widget()
                    add_copy_btn = widget.layout().itemAt(2).widget()
                    edit_btn.clicked.connect(lambda _, r=row: self.edit_book_row(r))
                    delete_btn.clicked.connect(lambda _, r=row: self.delete_book_row(r))
                    add_copy_btn.clicked.connect(lambda _, r=row: self.copy_controller.show_book_copies_dialog(r))
            
        except Exception as e:
            logging.error(f"Error loading books: {str(e)}")
            self.view.show_error(str(e))

    def show_add_book_dialog(self):
        dialog, fields = self.view.show_book_dialog()
        
        def save_book():
            book_data = {
                'title': fields['title'].text().strip(),
                'subtitle': fields['subtitle'].text().strip(),
                'author': fields['author'].text().strip(),
                'isbn': fields['isbn'].text().strip(),
                'publication_year': fields['publication_year'].value(),
                'publisher': fields['publisher'].text().strip(),
                'pages': fields['pages'].value(),
                'language': fields['language'].currentText(),
                'genre': fields['genre'].currentText(),
                'description': fields['description'].text().strip()
            }
            
            errors = self.model.validate_book_data(book_data)
            if errors:
                self.view.show_error("\n".join(errors))
                return
                
            try:
                self.model.add_book(book_data)
                self.load_books()
                dialog.accept()
            except ValueError as e:
                logging.error(f"Error adding book: {str(e)}")
                self.view.show_error(str(e))
        
        def scan_isbn():
            fields['isbn'].setFocus()
            fields['isbn'].clear()
        
        fields['save_button'].clicked.connect(save_book)
        fields['cancel_button'].clicked.connect(dialog.reject)
        fields['scan_button'].clicked.connect(scan_isbn)
        dialog.exec_()

    def show_edit_book_dialog(self):
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            self.view.show_error("Please select a book to edit")
            return
        self.edit_book_row(selected_rows[0].row())

    def edit_book_row(self, row):
        book_id = self.view.table.item(row, 0).text()
        book_data = {
            'title': self.view.table.item(row, 1).text() or '',
            'author': self.view.table.item(row, 2).text() or '',
            'isbn': self.view.table.item(row, 3).text() or '',
            'publication_year': int(self.view.table.item(row, 4).text()) if self.view.table.item(row, 4) and self.view.table.item(row, 4).text() else 0,
            'publisher': self.view.table.item(row, 5).text() or '',
            'pages': int(self.view.table.item(row, 6).text()) if self.view.table.item(row, 6) and self.view.table.item(row, 6).text() else 0,
            'genre': self.view.table.item(row, 7).text() or '',
            'subtitle': '',
            'language': 'English',
            'description': ''
        }
        
        dialog, fields = self.view.show_book_dialog(book_data)
        
        def save_book():
            updated_data = {
                'title': fields['title'].text().strip(),
                'subtitle': fields['subtitle'].text().strip(),
                'author': fields['author'].text().strip(),
                'isbn': fields['isbn'].text().strip(),
                'publication_year': fields['publication_year'].value(),
                'publisher': fields['publisher'].text().strip(),
                'pages': fields['pages'].value(),
                'language': fields['language'].currentText(),
                'genre': fields['genre'].currentText(),
                'description': fields['description'].text().strip()
            }
            
            errors = self.model.validate_book_data(updated_data)
            if errors:
                self.view.show_error("\n".join(errors))
                return
                
            try:
                self.model.update_book(int(book_id), updated_data)
                self.load_books()
                dialog.accept()
            except ValueError as e:
                logging.error(f"Error updating book: {str(e)}")
                self.view.show_error(str(e))
        
        def scan_isbn():
            fields['isbn'].setFocus()
            fields['isbn'].clear()
        
        fields['save_button'].clicked.connect(save_book)
        fields['cancel_button'].clicked.connect(dialog.reject)
        fields['scan_button'].clicked.connect(scan_isbn)
        dialog.exec_()

    def delete_book(self):
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            self.view.show_error("Please select a book to delete")
            return
        self.delete_book_row(selected_rows[0].row())

    def delete_book_row(self, row):
        reply = QMessageBox.question(
            self.view, 
            'Confirm Delete', 
            'Are you sure you want to delete this book?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                book_id = int(self.view.table.item(row, 0).text())
                self.model.delete_book(book_id)
                self.load_books()
            except ValueError as e:
                logging.error(f"Error deleting book: {str(e)}")
                self.view.show_error(str(e))

    def search_books(self):
        search_query = self.view.search_input.text().strip()
        genre = self.view.genre_filter.currentText()
        genre = None if genre == 'All' else genre
        year_min = self.view.year_min.value()
        year_max = self.view.year_max.value()
        self.load_books(search_query, genre, year_min, year_max)

    def clear_search(self):
        self.view.search_input.clear()
        self.view.genre_filter.setCurrentText('All')
        self.view.year_min.setValue(1000)
        self.view.year_max.setValue(datetime.now().year + 1)
        self.load_books()

    def import_books(self):
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Import Books", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    expected_fields = ['title', 'subtitle', 'author', 'isbn', 'publication_year', 'publisher', 'pages', 'language', 'genre', 'description']
                    if not all(field in expected_fields for field in reader.fieldnames):
                        self.view.show_error("CSV must contain valid book fields")
                        return
                    for row in reader:
                        book_data = {key: row.get(key, '') for key in expected_fields}
                        book_data['publication_year'] = int(book_data['publication_year']) if book_data['publication_year'] else 0
                        book_data['pages'] = int(book_data['pages']) if book_data['pages'] else 0
                        errors = self.model.validate_book_data(book_data)
                        if not errors:
                            self.model.add_book(book_data)
                        else:
                            logging.error(f"Error importing book {row.get('title', '')}: {', '.join(errors)}")
                            self.view.show_error(f"Error importing book {row.get('title', '')}: {', '.join(errors)}")
                self.load_books()
            except Exception as e:
                logging.error(f"Error importing books: {str(e)}")
                self.view.show_error(f"Error importing books: {str(e)}")

    def sort_table(self, column):
        columns = ['book_id', 'title', 'author', 'isbn', 'publication_year', 'publisher', 'pages', 'genre']
        # Prevent sorting on Copies (8) or Actions (9) columns
        if column >= len(columns):
            return
        selected_column = columns[column]
        self.current_sort_order = 'DESC' if self.current_sort_column == selected_column and self.current_sort_order == 'ASC' else 'ASC'
        self.current_sort_column = selected_column
        self.load_books(
            search_query=self.view.search_input.text().strip(),
            genre=None if self.view.genre_filter.currentText() == 'All' else self.view.genre_filter.currentText(),
            year_min=self.view.year_min.value(),
            year_max=self.view.year_max.value()
        )