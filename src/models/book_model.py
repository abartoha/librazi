from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime

class BookModel:
    def __init__(self, session_pool):
        self.session_pool = session_pool

    def get_books(self, search_query=None, sort_by='title', sort_order='ASC'):
        session = self.session_pool.get_session()
        try:
            query = """
                SELECT book_id, title, author, isbn, publication_year, publisher, pages, genre 
                FROM books 
                WHERE is_active = true
            """
            params = {}
            
            if search_query:
                query += " AND (title ILIKE :search OR author ILIKE :search OR isbn ILIKE :search OR genre ILIKE :search)"
                params['search'] = f'%{search_query}%'
                
            # Ensure valid sort_by column to prevent SQL injection
            valid_columns = ['book_id', 'title', 'author', 'isbn', 'publication_year', 'publisher', 'pages', 'genre']
            sort_by = sort_by if sort_by in valid_columns else 'title'
            sort_order = sort_order if sort_order in ['ASC', 'DESC'] else 'ASC'
            query += f" ORDER BY {sort_by} {sort_order}"
            
            result = session.execute(text(query), params)
            return result.fetchall()
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
            raise ValueError(f"Database error: {str(e)}")
        finally:
            self.session_pool.close_session(session)

    def validate_book_data(self, book_data):
        errors = []
        if not book_data.get('title') or len(book_data['title'].strip()) < 1:
            errors.append("Title is required")
        if not book_data.get('author') or len(book_data['author'].strip()) < 1:
            errors.append("Author is required")
        if book_data.get('isbn') and not (10 <= len(book_data['isbn'].replace('-', '')) <= 13):
            errors.append("ISBN must be 10 or 13 digits")
        if book_data.get('publication_year') and not (1000 < book_data['publication_year'] <= datetime.now().year + 1):
            errors.append(f"Publication year must be between 1000 and {datetime.now().year + 1}")
        if book_data.get('pages') and book_data['pages'] <= 0:
            errors.append("Pages must be greater than 0")
        return errors