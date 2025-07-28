from PyQt5.QtWidgets import QApplication
import sys
import logging
from db.session_pool import SessionPool
from models.copy_model import CopyModel
from models.book_model import BookModel
from views.book_management_view import BookManagementView
from controllers.book_controller import BookController
from controllers.copy_controller import CopyController
from views.main_window import MainWindow
from icon_manager import IconManager

logging.basicConfig(filename='book_management.log', level=logging.ERROR)

def main():
    try:
        app = QApplication(sys.argv)
        
        # Initialize session pool and models
        session_pool = SessionPool()
        book_model = BookModel(session_pool)
        copy_model = CopyModel(session_pool)
        
        # Initialize view
        book_view = BookManagementView()
        
        # Initialize controllers
        book_controller = BookController(book_model, book_view, None)  # Temporary None for copy_controller
        copy_controller = CopyController(copy_model, book_view, book_controller)
        book_controller.copy_controller = copy_controller  # Set reference
        
        # Initialize and show main window
        main_window = MainWindow(book_view)
        main_window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Application initialization failed: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()