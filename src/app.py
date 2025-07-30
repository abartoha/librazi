from PyQt5.QtWidgets import QApplication
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.copy_model import CopyModel
from models.book_model import BookModel
from models.member_model import MemberModel
from views.book_management_view import BookManagementView
from views.member_management_view import MemberManagementView
from controllers.book_controller import BookController
from controllers.copy_controller import CopyController
from controllers.member_controller import MemberController
from views.main_window import MainWindow
from icon_manager import IconManager

logging.basicConfig(filename='library_management.log', level=logging.ERROR)

def main():
    try:
        app = QApplication(sys.argv)
        
        # Initialize session pool
        engine = create_engine('sqlite:///library.db', echo=False)
        session_pool = scoped_session(sessionmaker(bind=engine))
        
        # Initialize models
        book_model = BookModel(session_pool)
        copy_model = CopyModel(session_pool)
        member_model = MemberModel(session_pool)
        
        # Initialize views
        book_view = BookManagementView()
        member_view = MemberManagementView()
        
        # Initialize controllers
        book_controller = BookController(book_model, book_view, None)
        copy_controller = CopyController(copy_model, book_view, book_controller)
        member_controller = MemberController(session_pool)
        book_controller.copy_controller = copy_controller
        
        # Initialize and show main window
        main_window = MainWindow(book_view, member_view)
        main_window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Application initialization failed: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()