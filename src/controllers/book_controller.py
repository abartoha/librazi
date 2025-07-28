from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

class BookController(QObject):
    search_triggered = pyqtSignal(str)
    
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
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
        self.view.table.horizontalHeader().sectionClicked.connect(self.sort_table)

    def load_books(self, search_query=None):
        try:
            books = self.model.get_books(search_query, self.current_sort_column, self.current_sort_order)
            self.view.show_books(books)
        except Exception as e:
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
                self.view.show_error(str(e))
        
        def scan_isbn():
            fields['isbn'].setFocus()  # Focus the ISBN field for scanner input
            fields['isbn'].clear()    # Clear existing text to prepare for scan
        
        fields['save_button'].clicked.connect(save_book)
        fields['cancel_button'].clicked.connect(dialog.reject)
        fields['scan_button'].clicked.connect(scan_isbn)
        dialog.exec_()

    def show_edit_book_dialog(self):
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            self.view.show_error("Please select a book to edit")
            return
            
        row = selected_rows[0].row()  # Get the first selected row
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
                self.view.show_error(str(e))
        
        def scan_isbn():
            fields['isbn'].setFocus()  # Focus the ISBN field for scanner input
            fields['isbn'].clear()    # Clear existing text to prepare for scan
        
        fields['save_button'].clicked.connect(save_book)
        fields['cancel_button'].clicked.connect(dialog.reject)
        fields['scan_button'].clicked.connect(scan_isbn)
        dialog.exec_()

    def delete_book(self):
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            self.view.show_error("Please select a book to delete")
            return
            
        reply = QMessageBox.question(
            self.view, 
            'Confirm Delete', 
            'Are you sure you want to delete this book?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                row = selected_rows[0].row()
                book_id = int(self.view.table.item(row, 0).text())
                self.model.delete_book(book_id)
                self.load_books()
            except ValueError as e:
                self.view.show_error(str(e))

    def search_books(self):
        search_query = self.view.search_input.text().strip()
        self.load_books(search_query)

    def sort_table(self, column):
        columns = ['book_id', 'title', 'author', 'isbn', 'publication_year', 'publisher', 'pages', 'genre']
        self.current_sort_column = columns[column]
        self.current_sort_order = 'DESC' if self.current_sort_order == 'ASC' else 'ASC'
        self.load_books(self.view.search_input.text().strip())