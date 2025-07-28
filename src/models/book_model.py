from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import logging

logging.basicConfig(filename='book_management.log', level=logging.ERROR)

class BookModel:
    def __init__(self, session_pool):
        self.session_pool = session_pool

    def get_books(self, search_query=None, genre=None, year_min=None, year_max=None, sort_by='title', sort_order='ASC'):
        session = self.session_pool.get_session()
        try:
            query = """
                SELECT book_id, title, author, isbn, publication_year, publisher, pages, genre,
                       created_at,
                       (SELECT COUNT(*) FROM book_copies bc WHERE bc.book_id = books.book_id AND bc.is_active = true) as copy_count
                FROM books 
                WHERE is_active = true
            """
            params = {}
            
            if search_query:
                query += " AND (title ILIKE :search OR author ILIKE :search OR isbn ILIKE :search OR genre ILIKE :search)"
                params['search'] = f'%{search_query}%'
            if genre and genre != 'All':  # Add the != 'All' check
                query += " AND genre = :genre"
                params['genre'] = genre
            if year_min:
                query += " AND publication_year >= :year_min"
                params['year_min'] = year_min
            if year_max:
                query += " AND publication_year <= :year_max"
                params['year_max'] = year_max
                
            valid_columns = ['book_id', 'title', 'author', 'isbn', 'publication_year', 'publisher', 'pages', 'genre']
            sort_by = sort_by if sort_by in valid_columns else 'title'
            sort_order = sort_order if sort_order in ['ASC', 'DESC'] else 'ASC'
            query += f" ORDER BY {sort_by} {sort_order}"
            
            result = session.execute(text(query), params)
            return result.fetchall()
        except Exception as e:
            logging.error(f"Error in get_books: {str(e)}")
            raise
        finally:
            self.session_pool.close_session(session)

    def add_book(self, book_data):
        session = self.session_pool.get_session()
        try:
            insert_sql = text("""
                INSERT INTO books (
                    title, subtitle, author, isbn, publication_year, publisher,
                    pages, language, genre, description, created_at
                )
                VALUES (
                    :title, :subtitle, :author, :isbn, :publication_year, :publisher,
                    :pages, :language, :genre, :description, CURRENT_TIMESTAMP
                )
                RETURNING book_id
            """)
            result = session.execute(insert_sql, book_data)
            session.commit()
            return result.scalar()
        except IntegrityError as e:
            session.rollback()
            logging.error(f"Error in add_book: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")
        finally:
            self.session_pool.close_session(session)

    def update_book(self, book_id, book_data):
        session = self.session_pool.get_session()
        try:
            update_sql = text("""
                UPDATE books 
                SET title = :title, 
                    subtitle = :subtitle, 
                    author = :author, 
                    isbn = :isbn,
                    publication_year = :publication_year,
                    publisher = :publisher,
                    pages = :pages,
                    language = :language,
                    genre = :genre,
                    description = :description,
                    updated_at = CURRENT_TIMESTAMP
                WHERE book_id = :book_id
                RETURNING book_id
            """)
            book_data['book_id'] = book_id
            result = session.execute(update_sql, book_data)
            session.commit()
            return result.scalar()
        except IntegrityError as e:
            session.rollback()
            logging.error(f"Error in update_book: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")
        finally:
            self.session_pool.close_session(session)

    def delete_book(self, book_id):
        session = self.session_pool.get_session()
        try:
            delete_sql = text("""
                UPDATE books 
                SET is_active = false,
                    updated_at = CURRENT_TIMESTAMP
                WHERE book_id = :book_id
                RETURNING book_id
            """)
            result = session.execute(delete_sql, {'book_id': book_id})
            session.commit()
            return result.scalar()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error in delete_book: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")
        finally:
            self.session_pool.close_session(session)

    def validate_isbn(self, isbn):
        if not isbn:
            return True
        isbn = isbn.replace('-', '').replace(' ', '')
        if len(isbn) == 10:
            total = sum((10 - i) * (10 if c == 'X' else int(c)) for i, c in enumerate(isbn[:9]))
            check_digit = (11 - (total % 11)) % 11 == (10 if isbn[-1] == 'X' else int(isbn[-1]))
            return check_digit
        elif len(isbn) == 13:
            total = sum((3 if i % 2 else 1) * int(c) for i, c in enumerate(isbn[:12]))
            check_digit = (10 - (total % 10)) % 10 == int(isbn[-1])
            return check_digit
        return False

    def validate_book_data(self, book_data):
        errors = []
        if not book_data.get('title') or len(book_data['title'].strip()) < 1:
            errors.append("Title is required")
        if book_data.get('title') and len(book_data['title']) > 255:
            errors.append("Title must be 255 characters or less")
        if not book_data.get('author') or len(book_data['author'].strip()) < 1:
            errors.append("Author is required")
        if book_data.get('author') and len(book_data['author']) > 255:
            errors.append("Author must be 255 characters or less")
        if book_data.get('isbn') and not self.validate_isbn(book_data['isbn']):
            errors.append("Invalid ISBN checksum")
        if book_data.get('publication_year') and not (1000 < book_data['publication_year'] <= datetime.now().year + 1):
            errors.append(f"Publication year must be between 1000 and {datetime.now().year + 1}")
        if book_data.get('pages') and book_data['pages'] <= 0:
            errors.append("Pages must be greater than 0")
        if book_data.get('publisher') and len(book_data['publisher']) > 255:
            errors.append("Publisher must be 255 characters or less")
        if book_data.get('subtitle') and len(book_data['subtitle']) > 255:
            errors.append("Subtitle must be 255 characters or less")
        if book_data.get('description') and len(book_data['description']) > 1000:
            errors.append("Description must be 1000 characters or less")
        return errors