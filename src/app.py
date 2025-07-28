from PyQt5.QtWidgets import QApplication
from db.session_pool import SessionPool
from models.copy_model import CopyModel
from models.book_model import BookModel
from views.book_management_view import BookManagementView
from controllers.book_controller import BookController
from controllers.copy_controller import CopyController
from views.main_window import MainWindow

def main():
    import sys
    app = QApplication(sys.argv)
    session_pool = SessionPool()
    book_model = BookModel(session_pool)
    copy_model = CopyModel(session_pool)
    book_view = BookManagementView()
    copy_controller = CopyController(   copy_model, book_view, None)  # Temporary, no book_controller yet
    book_controller = BookController(book_model, book_view, copy_controller)
    copy_controller.book_controller = book_controller  # Set reference
    main_window = MainWindow(book_view)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()