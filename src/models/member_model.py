import logging
import re
from datetime import datetime, date, timedelta
from sqlalchemy import text, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class MemberModel:
    def __init__(self, session_pool):
        self.session_pool = session_pool
        
    def get_members(self, search_query=None, status=None, membership_type=None, 
                   sort_by='last_name', sort_order='ASC'):
        """Retrieve members with loan counts and fine totals"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT m.member_id, m.member_number, 
                           m.first_name, m.last_name,
                           m.email, m.phone, m.membership_status,
                           m.membership_date, m.membership_expiry,
                           COUNT(DISTINCT l.loan_id) as active_loans,
                           COALESCE(SUM(f.amount), 0) as total_outstanding_fines,
                           MAX(l.loan_date) as last_activity
                    FROM members m
                    LEFT JOIN loans l ON m.member_id = l.member_id AND l.loan_status = 'active'
                    LEFT JOIN fines f ON m.member_id = f.member_id AND f.fine_status = 'pending'
                    WHERE m.is_active = true
                    GROUP BY m.member_id
                """)
                
                params = {}
                if search_query:
                    query = text(str(query) + """
                        AND (m.first_name ILIKE :search 
                             OR m.last_name ILIKE :search 
                             OR m.email ILIKE :search 
                             OR m.member_number ILIKE :search 
                             OR m.phone ILIKE :search)
                    """)
                    params['search'] = f'%{search_query}%'
                
                if status:
                    query = text(str(query) + " AND m.membership_status = :status")
                    params['status'] = status
                
                if membership_type:
                    query = text(str(query) + " AND m.membership_type = :membership_type")
                    params['membership_type'] = membership_type
                
                if sort_by in ['member_id', 'member_number', 'first_name', 'last_name', 
                              'email', 'phone', 'membership_status', 'membership_date',
                              'membership_expiry', 'active_loans', 'total_outstanding_fines',
                              'last_activity']:
                    query = text(str(query) + f" ORDER BY m.{sort_by} {sort_order}")
                
                result = session.execute(query, params).fetchall()
                return [
                    (row.member_id, row.member_number, (row.first_name, row.last_name),
                     row.email, row.phone, row.membership_status, row.membership_date,
                     row.membership_expiry, row.active_loans, row.total_outstanding_fines,
                     row.last_activity)
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"Error retrieving members: {str(e)}")
            raise
    
    def add_member(self, member_data):
        """Add a new member to the database"""
        try:
            with self.session_pool() as session:
                insert_query = text("""
                    INSERT INTO members (
                        member_number, first_name, last_name, email, phone,
                        date_of_birth, address, membership_date, membership_expiry,
                        membership_status, max_books_allowed, max_renewal_allowed,
                        emergency_contact_name, emergency_contact_phone, member_notes,
                        is_active
                    ) VALUES (
                        :member_number, :first_name, :last_name, :email, :phone,
                        :date_of_birth, :address, :membership_date, :membership_expiry,
                        :membership_status, :max_books_allowed, :max_renewal_allowed,
                        :emergency_contact_name, :emergency_contact_phone, :member_notes,
                        true
                    ) RETURNING member_id
                """)
                
                result = session.execute(insert_query, member_data)
                session.commit()
                return result.scalar()
                
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error adding member: {str(e)}")
            raise ValueError("Member number or email already exists")
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding member: {str(e)}")
            raise
    
    def update_member(self, member_id, member_data):
        """Update existing member data"""
        try:
            with self.session_pool() as session:
                update_query = text("""
                    UPDATE members
                    SET first_name = :first_name,
                        last_name = :last_name,
                        email = :email,
                        phone = :phone,
                        date_of_birth = :date_of_birth,
                        address = :address,
                        membership_date = :membership_date,
                        membership_expiry = :membership_expiry,
                        membership_status = :membership_status,
                        max_books_allowed = :max_books_allowed,
                        max_renewal_allowed = :max_renewal_allowed,
                        emergency_contact_name = :emergency_contact_name,
                        emergency_contact_phone = :emergency_contact_phone,
                        member_notes = :member_notes
                    WHERE member_id = :member_id
                """)
                
                member_data['member_id'] = member_id
                session.execute(update_query, member_data)
                session.commit()
                
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error updating member: {str(e)}")
            raise ValueError("Email already exists")
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating member: {str(e)}")
            raise
    
    def delete_member(self, member_id):
        """Soft delete a member"""
        try:
            with self.session_pool() as session:
                # Check for active loans
                loan_check = session.execute(
                    text("SELECT COUNT(*) FROM loans WHERE member_id = :member_id AND loan_status = 'active'"),
                    {'member_id': member_id}
                ).scalar()
                
                if loan_check > 0:
                    raise ValueError("Cannot delete member with active loans")
                
                session.execute(
                    text("UPDATE members SET is_active = false WHERE member_id = :member_id"),
                    {'member_id': member_id}
                )
                session.commit()
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting member: {str(e)}")
            raise
    
    def renew_membership(self, member_id, new_expiry_date):
        """Renew membership with new expiry date"""
        try:
            with self.session_pool() as session:
                session.execute(
                    text("""
                        UPDATE members
                        SET membership_expiry = :new_expiry_date,
                            membership_status = 'active'
                        WHERE member_id = :member_id
                    """),
                    {'member_id': member_id, 'new_expiry_date': new_expiry_date}
                )
                session.commit()
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error renewing membership: {str(e)}")
            raise
    
    def get_member_loans(self, member_id):
        """Get complete loan history for a member"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT l.loan_id, b.title, l.loan_date, l.due_date,
                           l.return_date, l.loan_status, l.renewal_count
                    FROM loans l
                    JOIN book_copies bc ON l.copy_id = bc.copy_id
                    JOIN books b ON bc.book_id = b.book_id
                    WHERE l.member_id = :member_id
                    ORDER BY l.loan_date DESC
                """)
                
                result = session.execute(query, {'member_id': member_id}).fetchall()
                return [
                    (row.loan_id, row.title, row.loan_date, row.due_date,
                     row.return_date, row.loan_status, row.renewal_count)
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"Error retrieving member loans: {str(e)}")
            raise
    
    def get_member_fines(self, member_id):
        """Get outstanding fines for a member"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT f.fine_id, f.amount, f.fine_date, f.fine_status, f.description
                    FROM fines f
                    WHERE f.member_id = :member_id AND f.fine_status = 'pending'
                    ORDER BY f.fine_date DESC
                """)
                
                result = session.execute(query, {'member_id': member_id}).fetchall()
                return [
                    (row.fine_id, row.amount, row.fine_date, row.fine_status, row.description)
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"Error retrieving member fines: {str(e)}")
            raise
    
    def check_member_eligibility(self, member_id):
        """Check if member can borrow books"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT m.membership_status, m.max_books_allowed,
                           COUNT(l.loan_id) as active_loans,
                           COALESCE(SUM(f.amount), 0) as total_fines
                    FROM members m
                    LEFT JOIN loans l ON m.member_id = l.member_id AND l.loan_status = 'active'
                    LEFT JOIN fines f ON m.member_id = f.member_id AND f.fine_status = 'pending'
                    WHERE m.member_id = :member_id AND m.is_active = true
                    GROUP BY m.member_id
                """)
                
                result = session.execute(query, {'member_id': member_id}).fetchone()
                if not result:
                    return False, "Member not found or inactive"
                
                if result.membership_status != 'active':
                    return False, "Member status is not active"
                
                if result.active_loans >= result.max_books_allowed:
                    return False, "Maximum book limit reached"
                
                if result.total_fines > 50.00:  # Example fine limit
                    return False, "Outstanding fines exceed limit"
                
                return True, "Member eligible to borrow"
                
        except Exception as e:
            logger.error(f"Error checking member eligibility: {str(e)}")
            raise
    
    def validate_member_data(self, member_data):
        """Validate member data before saving"""
        errors = []
        
        # Required fields
        if not member_data['first_name']:
            errors.append("First name is required")
        if not member_data['last_name']:
            errors.append("Last name is required")
        if not member_data['email']:
            errors.append("Email is required")
            
        # Length validations
        if len(member_data['first_name']) > 100:
            errors.append("First name must be 100 characters or less")
        if len(member_data['last_name']) > 100:
            errors.append("Last name must be 100 characters or less")
        if len(member_data['email']) > 255:
            errors.append("Email must be 255 characters or less")
            
        # Format validations
        if member_data['email'] and not self.validate_email(member_data['email']):
            errors.append("Invalid email format")
        if member_data['phone'] and not self.validate_phone(member_data['phone']):
            errors.append("Invalid phone number format")
            
        # Date validations
        try:
            dob = datetime.strptime(member_data['date_of_birth'], '%Y-%m-%d').date()
            if dob > date.today().replace(year=date.today().year-1):
                errors.append("Date of birth must be at least 1 year ago")
        except ValueError:
            errors.append("Invalid date of birth format")
            
        try:
            membership_date = datetime.strptime(member_data['membership_date'], '%Y-%m-%d').date()
            if membership_date > date.today():
                errors.append("Membership date cannot be in the future")
        except ValueError:
            errors.append("Invalid membership date format")
            
        try:
            expiry_date = datetime.strptime(member_data['membership_expiry'], '%Y-%m-%d').date()
            if expiry_date < membership_date:
                errors.append("Expiry date must be after membership date")
        except ValueError:
            errors.append("Invalid expiry date format")
            
        # Numeric validations
        if not 1 <= member_data['max_books_allowed'] <= 20:
            errors.append("Maximum books allowed must be between 1 and 20")
        if not 0 <= member_data['max_renewal_allowed'] <= 10:
            errors.append("Maximum renewals allowed must be between 0 and 10")
            
        # Uniqueness checks
        if member_data['member_number'] and not self.is_member_number_unique(
            member_data['member_number'], 
            member_data.get('member_id')
        ):
            errors.append("Member number already exists")
            
        if not self.is_email_unique(
            member_data['email'],
            member_data.get('member_id')
        ):
            errors.append("Email address already exists")
            
        return errors
    
    def validate_email(self, email):
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone)) if phone else True
    
    def is_member_number_unique(self, member_number, exclude_member_id=None):
        """Check if member number is unique"""
        try:
            with self.session_pool() as session:
                query = text("SELECT COUNT(*) FROM members WHERE member_number = :member_number AND is_active = true")
                params = {'member_number': member_number}
                if exclude_member_id:
                    query = text(str(query) + " AND member_id != :member_id")
                    params['member_id'] = exclude_member_id
                return session.execute(query, params).scalar() == 0
        except Exception as e:
            logger.error(f"Error checking member number uniqueness: {str(e)}")
            raise
    
    def is_email_unique(self, email, exclude_member_id=None):
        """Check if email is unique"""
        try:
            with self.session_pool() as session:
                query = text("SELECT COUNT(*) FROM members WHERE email = :email AND is_active = true")
                params = {'email': email}
                if exclude_member_id:
                    query = text(str(query) + " AND member_id != :member_id")
                    params['member_id'] = exclude_member_id
                return session.execute(query, params).scalar() == 0
        except Exception as e:
            logger.error(f"Error checking email uniqueness: {str(e)}")
            raise
    
    def generate_unique_member_number(self):
        """Generate a unique member number"""
        try:
            with self.session_pool() as session:
                year = datetime.now().year
                base_number = f"MEM-{year}-"
                query = text("SELECT member_number FROM members WHERE member_number LIKE :pattern ORDER BY member_number DESC LIMIT 1")
                
                result = session.execute(query, {'pattern': f'{base_number}%'}).scalar()
                if result:
                    last_num = int(result.split('-')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                new_member_number = f"{base_number}{new_num:04d}"
                while not self.is_member_number_unique(new_member_number):
                    new_num += 1
                    new_member_number = f"{base_number}{new_num:04d}"
                    
                return new_member_number
                
        except Exception as e:
            logger.error(f"Error generating member number: {str(e)}")
            raise
    
    def get_member_by_id(self, member_id):
        """Get member details by ID"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT member_id, member_number, first_name, last_name, email, phone,
                           date_of_birth, address, membership_date, membership_expiry,
                           membership_status, max_books_allowed, max_renewal_allowed,
                           emergency_contact_name, emergency_contact_phone, member_notes
                    FROM members
                    WHERE member_id = :member_id AND is_active = true
                """)
                
                result = session.execute(query, {'member_id': member_id}).fetchone()
                if not result:
                    return None
                    
                return {
                    'member_id': result.member_id,
                    'member_number': result.member_number,
                    'first_name': result.first_name,
                    'last_name': result.last_name,
                    'email': result.email,
                    'phone': result.phone,
                    'date_of_birth': result.date_of_birth,
                    'address': result.address,
                    'membership_date': result.membership_date,
                    'membership_expiry': result.membership_expiry,
                    'membership_status': result.membership_status,
                    'max_books_allowed': result.max_books_allowed,
                    'max_renewal_allowed': result.max_renewal_allowed,
                    'emergency_contact_name': result.emergency_contact_name,
                    'emergency_contact_phone': result.emergency_contact_phone,
                    'member_notes': result.member_notes
                }
                
        except Exception as e:
            logger.error(f"Error retrieving member: {str(e)}")
            raise
    
    def get_membership_statistics(self):
        """Get membership statistics"""
        try:
            with self.session_pool() as session:
                query = text("""
                    SELECT 
                        COUNT(*) as total_members,
                        COUNT(CASE WHEN membership_status = 'active' THEN 1 END) as active_members,
                        COUNT(CASE WHEN membership_expiry <= :soon THEN 1 END) as expiring_soon,
                        COUNT(CASE WHEN membership_status = 'expired' THEN 1 END) as expired_members
                    FROM members
                    WHERE is_active = true
                """)
                
                result = session.execute(query, {'soon': date.today() + timedelta(days=30)}).fetchone()
                return {
                    'total_members': result.total_members,
                    'active_members': result.active_members,
                    'expiring_soon': result.expiring_soon,
                    'expired_members': result.expired_members
                }
                
        except Exception as e:
            logger.error(f"Error retrieving membership statistics: {str(e)}")
            raise