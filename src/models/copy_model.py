from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import logging

logging.basicConfig(filename='book_management.log', level=logging.ERROR)

class CopyModel:
    def __init__(self, session_pool):
        self.session_pool = session_pool

    def get_book_copies(self, book_id):
        session = self.session_pool.get_session()
        try:
            query = """
                SELECT copy_id, book_id, copy_number, acquisition_date, current_condition, 
                       status, is_active
                FROM book_copies 
                WHERE book_id = :book_id AND is_active = true
                ORDER BY copy_number
            """
            result = session.execute(text(query), {'book_id': book_id})
            return result.fetchall()
        except Exception as e:
            logging.error(f"Error in get_book_copies: {str(e)}")
            raise
        finally:
            self.session_pool.close_session(session)

    def add_book_copy(self, book_id, copy_data):
        session = self.session_pool.get_session()
        try:
            # Check for duplicate copy_number
            existing = session.execute(text(
                "SELECT 1 FROM book_copies WHERE book_id = :book_id AND copy_number = :copy_number AND is_active = true"
            ), {'book_id': book_id, 'copy_number': copy_data['copy_number']}).scalar()
            if existing:
                raise ValueError("Copy number already exists for this book")
                
            insert_sql = text("""
                INSERT INTO book_copies (
                    book_id, copy_number, acquisition_date, current_condition,
                    status, is_active, created_at
                )
                VALUES (
                    :book_id, :copy_number, :acquisition_date, :current_condition,
                    :status, true, CURRENT_TIMESTAMP
                )
                RETURNING copy_id
            """)
            copy_data['book_id'] = book_id
            result = session.execute(insert_sql, copy_data)
            session.commit()
            return result.scalar()
        except IntegrityError as e:
            session.rollback()
            logging.error(f"Error in add_book_copy: {str(e)}")
            raise ValueError("Failed to add copy: Duplicate or invalid data")
        except ValueError as e:
            session.rollback()
            raise
        finally:
            self.session_pool.close_session(session)

    def update_book_copy(self, copy_id, copy_data):
        session = self.session_pool.get_session()
        try:
            update_sql = text("""
                UPDATE book_copies 
                SET copy_number = :copy_number,
                    acquisition_date = :acquisition_date,
                    current_condition = :current_condition,
                    status = :status,
                    updated_at = CURRENT_TIMESTAMP
                WHERE copy_id = :copy_id
                RETURNING copy_id
            """)
            copy_data['copy_id'] = copy_id
            result = session.execute(update_sql, copy_data)
            session.commit()
            return result.scalar()
        except IntegrityError as e:
            session.rollback()
            logging.error(f"Error in update_book_copy: {str(e)}")
            raise ValueError("Failed to update copy: Duplicate or invalid data")
        finally:
            self.session_pool.close_session(session)

    def delete_book_copy(self, copy_id):
        session = self.session_pool.get_session()
        try:
            delete_sql = text("""
                UPDATE book_copies 
                SET is_active = false,
                    updated_at = CURRENT_TIMESTAMP
                WHERE copy_id = :copy_id
                RETURNING copy_id
            """)
            result = session.execute(delete_sql, {'copy_id': copy_id})
            session.commit()
            return result.scalar()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error in delete_book_copy: {str(e)}")
            raise ValueError("Failed to delete copy")
        finally:
            self.session_pool.close_session(session)

    def validate_book_copy_data(self, copy_data, book_id):
        errors = []
        if not copy_data.get('copy_number') or len(copy_data['copy_number'].strip()) < 1:
            errors.append("Copy number is required")
        if copy_data.get('copy_number') and len(copy_data['copy_number']) > 50:
            errors.append("Copy number must be 50 characters or less")
        if not copy_data.get('acquisition_date'):
            errors.append("Acquisition date is required")
        else:
            try:
                acq_date = datetime.strptime(copy_data['acquisition_date'], '%Y-%m-%d')
                if acq_date > datetime.now():
                    errors.append("Acquisition date cannot be in the future")
            except ValueError:
                errors.append("Invalid acquisition date format")
        if copy_data.get('current_condition') and copy_data['current_condition'] not in ['excellent', 'good', 'fair', 'poor']:
            errors.append("Condition must be excellent, good, fair, or poor")
        if copy_data.get('status') and copy_data['status'] not in ['available', 'loaned', 'reserved', 'lost']:
            errors.append("Status must be available, loaned, reserved, or lost")
        return errors