from PyQt5.QtCore import QObject, QDate, Qt
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

class CopyController(QObject):
    def __init__(self, copy_model, view, book_controller):
        super().__init__()
        self.copy_model = copy_model
        self.view = view
        self.book_controller = book_controller

    def show_book_copies_dialog(self, row):
        book_id = int(self.view.table.item(row, 0).text())
        book_title = self.view.table.item(row, 1).text()
        dialog, fields = self.view.show_book_copies_dialog(book_id, book_title)
        
        def load_copies():
            try:
                copies = self.copy_model.get_book_copies(book_id)
                self.view.copies_table.setRowCount(len(copies))
                for row_idx, copy in enumerate(copies):
                    # copy_id, book_id, copy_number, acquisition_date, current_condition, status, is_active
                    values = [copy[0], copy[2], copy[3], copy[4], copy[5]]
                    for col_idx, value in enumerate(values):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.view.copies_table.setItem(row_idx, col_idx, item)
                self.view.copies_table.resizeColumnsToContents()
            except Exception as e:
                self.view.show_error(f"Error loading book copies: {str(e)}")
        
        def add_copy():
            copy_dialog, copy_fields = self.view.show_book_copy_dialog(book_id)
            
            def save_copy():
                copy_data = {
                    'copy_number': copy_fields['copy_number'].text().strip(),
                    'acquisition_date': copy_fields['acquisition_date'].date().toString('yyyy-MM-dd'),
                    'current_condition': copy_fields['current_condition'].currentText(),
                    'status': copy_fields['status'].currentText()
                }
                
                errors = self.copy_model.validate_book_copy_data(copy_data, book_id)
                if errors:
                    self.view.show_error("\n".join(errors))
                    return
                
                try:
                    self.copy_model.add_book_copy(book_id, copy_data)
                    load_copies()
                    self.book_controller.load_books()  # Refresh main table for copy count
                    copy_dialog.accept()
                except ValueError as e:
                    self.view.show_error(str(e))
            
            copy_fields['save_button'].clicked.connect(save_copy)
            copy_fields['cancel_button'].clicked.connect(copy_dialog.reject)
            copy_dialog.exec_()
        
        def edit_copy():
            selected_rows = self.view.copies_table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a copy to edit")
                return
                
            row_idx = selected_rows[0].row()
            copy_id = self.view.copies_table.item(row_idx, 0).text()
            try:
                copy_data = {
                    'copy_number': self.view.copies_table.item(row_idx, 1).text() or '',
                    'acquisition_date': QDate.fromString(
                        self.view.copies_table.item(row_idx, 2).text() or QDate.currentDate().toString('yyyy-MM-dd'), 
                        'yyyy-MM-dd'
                    ),
                    'current_condition': self.view.copies_table.item(row_idx, 3).text() or 'excellent',
                    'status': self.view.copies_table.item(row_idx, 4).text() or 'available'
                }
            except ValueError:
                self.view.show_error("Invalid data in selected copy")
                return
                
            copy_dialog, copy_fields = self.view.show_book_copy_dialog(book_id, copy_data)
            
            def save_copy():
                updated_data = {
                    'copy_number': copy_fields['copy_number'].text().strip(),
                    'acquisition_date': copy_fields['acquisition_date'].date().toString('yyyy-MM-dd'),
                    'current_condition': copy_fields['current_condition'].currentText(),
                    'status': copy_fields['status'].currentText()
                }
                
                errors = self.copy_model.validate_book_copy_data(updated_data, book_id)
                if errors:
                    self.view.show_error("\n".join(errors))
                    return
                
                try:
                    self.copy_model.update_book_copy(int(copy_id), updated_data)
                    load_copies()
                    self.book_controller.load_books()
                    copy_dialog.accept()
                except ValueError as e:
                    self.view.show_error(str(e))
            
            copy_fields['save_button'].clicked.connect(save_copy)
            copy_fields['cancel_button'].clicked.connect(copy_dialog.reject)
            copy_dialog.exec_()
        
        def delete_copy():
            selected_rows = self.view.copies_table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a copy to delete")
                return
                
            reply = QMessageBox.question(
                dialog, 
                'Confirm Delete', 
                'Are you sure you want to delete this book copy?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    row_idx = selected_rows[0].row()
                    copy_id = int(self.view.copies_table.item(row_idx, 0).text())
                    self.copy_model.delete_book_copy(copy_id)
                    load_copies()
                    self.book_controller.load_books()
                except ValueError as e:
                    self.view.show_error(str(e))
        
        load_copies()
        fields['add_button'].clicked.connect(add_copy)
        fields['edit_button'].clicked.connect(edit_copy)
        fields['delete_button'].clicked.connect(delete_copy)
        fields['close_button'].clicked.connect(dialog.reject)
        dialog.exec_()