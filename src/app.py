from PyQt5.QtWidgets import QApplication
from db.session_pool import SessionPool
from models.book_model import BookModel
from views.book_management_view import BookManagementView
from controllers.book_controller import BookController
from views.main_window import MainWindow

def main():
    import sys
    app = QApplication(sys.argv)
    session_pool = SessionPool()
    book_model = BookModel(session_pool)
    book_view = BookManagementView()
    book_controller = BookController(book_model, book_view)
    main_window = MainWindow(book_view)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()