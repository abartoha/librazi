import logging
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime
from models.member_model import MemberModel
from views.member_management_view import MemberManagementView, StyledToolButton

logger = logging.getLogger(__name__)

class MemberController:
    def __init__(self, session_pool):
        self.model = MemberModel(session_pool)
        self.view = MemberManagementView()
        self.connect_signals()
        
    def connect_signals(self):
        """Connect all UI signals to their handlers"""
        # Search and filter signals
        self.view.search_button.clicked.connect(self.handle_search)
        self.view.clear_search_button.clicked.connect(self.clear_search)
        self.view.search_input.returnPressed.connect(self.handle_search)
        self.view.membership_status_filter.currentTextChanged.connect(self.handle_search)
        self.view.membership_type_filter.currentTextChanged.connect(self.handle_search)
        
        # Action button signals
        self.view.add_button.clicked.connect(self.show_add_member_dialog)
        self.view.edit_button.clicked.connect(self.show_edit_member_dialog)
        self.view.delete_button.clicked.connect(self.handle_delete_member)
        self.view.renew_button.clicked.connect(self.show_renewal_dialog)
        self.view.import_button.clicked.connect(self.handle_import_members)
        
        # Table selection signal
        self.view.table.selectionModel().selectionChanged.connect(self.update_button_states)
        
        # Initial load
        self.refresh_members()
        
    def connect_action_buttons(self, row_idx):
        """Connect signals for action buttons in a table row"""
        widget = self.view.table.cellWidget(row_idx, 11)
        if widget:
            edit_btn = widget.findChild(StyledToolButton, property_filter={'button_type': 'edit'})
            delete_btn = widget.findChild(StyledToolButton, property_filter={'button_type': 'delete'})
            renew_btn = widget.findChild(StyledToolButton, property_filter={'button_type': 'renew'})
            view_loans_btn = widget.findChild(StyledToolButton, property_filter={'button_type': 'view'})
            
            if edit_btn:
                edit_btn.clicked.connect(lambda: self.show_edit_member_dialog(edit_btn.property('member_id')))
            if delete_btn:
                delete_btn.clicked.connect(lambda: self.handle_delete_member(delete_btn.property('member_id')))
            if renew_btn:
                renew_btn.clicked.connect(lambda: self.show_renewal_dialog(renew_btn.property('member_id')))
            if view_loans_btn:
                view_loans_btn.clicked.connect(lambda: self.show_member_loans_dialog(view_loans_btn.property('member_id')))
    
    def disconnect_action_buttons(self, row_idx):
        """Disconnect signals for action buttons in a table row"""
        widget = self.view.table.cellWidget(row_idx, 11)
        if widget:
            for btn in widget.findChildren(StyledToolButton):
                try:
                    btn.clicked.disconnect()
                except:
                    pass
    
    def refresh_members(self):
        """Refresh member table with current filters"""
        try:
            search_query = self.view.search_input.text().strip()
            status = self.view.membership_status_filter.currentText()
            membership_type = self.view.membership_type_filter.currentText()
            
            status = None if status == 'All' else status.lower()
            membership_type = None if membership_type == 'All' else membership_type.lower()
            
            members = self.model.get_members(
                search_query=search_query or None,
                status=status,
                membership_type=membership_type
            )
            
            self.view.show_members(members)
            
            # Reconnect action buttons for all rows
            for row in range(self.view.table.rowCount()):
                self.disconnect_action_buttons(row)
                self.connect_action_buttons(row)
                
        except Exception as e:
            logger.error(f"Error refreshing members: {str(e)}")
            self.view.show_error(f"Failed to load members: {str(e)}")
    
    def handle_search(self):
        """Handle search button click"""
        self.refresh_members()
    
    def clear_search(self):
        """Clear search filters and refresh"""
        self.view.search_input.clear()
        self.view.membership_status_filter.setCurrentText('All')
        self.view.membership_type_filter.setCurrentText('All')
        self.refresh_members()
    
    def show_add_member_dialog(self):
        """Show dialog for adding new member"""
        dialog, fields = self.view.show_member_dialog()
        
        def handle_save():
            try:
                member_data = self.validate_member_form(fields)
                if member_data:
                    new_member_id = self.model.add_member(member_data)
                    self.view.show_success("Member added successfully!")
                    self.refresh_members()
                    dialog.accept()
            except ValueError as e:
                self.view.show_error(str(e))
            except Exception as e:
                logger.error(f"Error adding member: {str(e)}")
                self.view.show_error(f"Failed to add member: {str(e)}")
        
        fields['save_button'].clicked.connect(handle_save)
        fields['cancel_button'].clicked.connect(dialog.reject)
        dialog.exec_()
    
    def show_edit_member_dialog(self, member_id=None):
        """Show dialog for editing existing member"""
        if not member_id:
            selected_rows = self.view.table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a member to edit")
                return
            member_id = self.view.table.item(selected_rows[0].row(), 0).text()
        
        try:
            member_data = self.model.get_member_by_id(member_id)
            if not member_data:
                self.view.show_error("Member not found")
                return
                
            dialog, fields = self.view.show_member_dialog(member_data)
            
            def handle_save():
                try:
                    updated_data = self.validate_member_form(fields)
                    if updated_data:
                        self.model.update_member(member_id, updated_data)
                        self.view.show_success("Member updated successfully!")
                        self.refresh_members()
                        dialog.accept()
                except ValueError as e:
                    self.view.show_error(str(e))
                except Exception as e:
                    logger.error(f"Error updating member: {str(e)}")
                    self.view.show_error(f"Failed to update member: {str(e)}")
            
            fields['save_button'].clicked.connect(handle_save)
            fields['cancel_button'].clicked.connect(dialog.reject)
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Error loading member for edit: {str(e)}")
            self.view.show_error(f"Failed to load member: {str(e)}")
    
    def handle_delete_member(self, member_id=None):
        """Handle member deletion with confirmation"""
        if not member_id:
            selected_rows = self.view.table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a member to delete")
                return
            member_id = self.view.table.item(selected_rows[0].row(), 0).text()
        
        try:
            member_data = self.model.get_member_by_id(member_id)
            if not member_data:
                self.view.show_error("Member not found")
                return
                
            reply = QMessageBox.question(
                self.view,
                "Confirm Deletion",
                f"Are you sure you want to delete member {member_data['first_name']} {member_data['last_name']}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.model.delete_member(member_id)
                self.view.show_success("Member deleted successfully!")
                self.refresh_members()
                
        except ValueError as e:
            self.view.show_error(str(e))
        except Exception as e:
            logger.error(f"Error deleting member: {str(e)}")
            self.view.show_error(f"Failed to delete member: {str(e)}")
    
    def show_renewal_dialog(self, member_id=None):
        """Show membership renewal dialog"""
        if not member_id:
            selected_rows = self.view.table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a member to renew")
                return
            member_id = self.view.table.item(selected_rows[0].row(), 0).text()
        
        try:
            member_data = self.model.get_member_by_id(member_id)
            if not member_data:
                self.view.show_error("Member not found")
                return
                
            dialog, fields = self.view.show_renewal_dialog(
                member_id,
                f"{member_data['first_name']} {member_data['last_name']}",
                member_data['membership_expiry']
            )
            
            def handle_renew():
                try:
                    new_expiry = fields['new_expiry'].date().toString('yyyy-MM-dd')
                    self.model.renew_membership(member_id, new_expiry)
                    self.view.show_success("Membership renewed successfully!")
                    self.refresh_members()
                    dialog.accept()
                except Exception as e:
                    logger.error(f"Error renewing membership: {str(e)}")
                    self.view.show_error(f"Failed to renew membership: {str(e)}")
            
            fields['renew_button'].clicked.connect(handle_renew)
            fields['cancel_button'].clicked.connect(dialog.reject)
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Error loading renewal dialog: {str(e)}")
            self.view.show_error(f"Failed to load renewal dialog: {str(e)}")
    
    def show_member_loans_dialog(self, member_id=None):
        """Show member's loan history dialog"""
        if not member_id:
            selected_rows = self.view.table.selectionModel().selectedRows()
            if not selected_rows:
                self.view.show_error("Please select a member to view loans")
                return
            member_id = self.view.table.item(selected_rows[0].row(), 0).text()
        
        try:
            member_data = self.model.get_member_by_id(member_id)
            if not member_data:
                self.view.show_error("Member not found")
                return
                
            loans = self.model.get_member_loans(member_id)
            dialog = self.view.show_member_loans_dialog(
                member_id,
                f"{member_data['first_name']} {member_data['last_name']}",
                loans
            )
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Error loading member loans: {str(e)}")
            self.view.show_error(f"Failed to load member loans: {str(e)}")
    
    def handle_import_members(self):
        """Placeholder for import members functionality"""
        self.view.show_error("Import functionality not implemented yet")
    
    def validate_member_form(self, fields):
        """Validate member form data"""
        member_data = {
            'member_number': fields['member_number'].text().strip(),
            'first_name': fields['first_name'].text().strip(),
            'last_name': fields['last_name'].text().strip(),
            'email': fields['email'].text().strip(),
            'phone': fields['phone'].text().strip(),
            'date_of_birth': fields['date_of_birth'].date().toString('yyyy-MM-dd'),
            'address': fields['address'].toPlainText().strip(),
            'membership_date': fields['membership_date'].date().toString('yyyy-MM-dd'),
            'membership_expiry': fields['membership_expiry'].date().toString('yyyy-MM-dd'),
            'membership_status': fields['membership_status'].currentText().lower(),
            'max_books_allowed': fields['max_books_allowed'].value(),
            'max_renewal_allowed': fields['max_renewal_allowed'].value(),
            'emergency_contact_name': fields['emergency_contact_name'].text().strip(),
            'emergency_contact_phone': fields['emergency_contact_phone'].text().strip(),
            'member_notes': fields['member_notes'].toPlainText().strip()
        }
        
        errors = self.model.validate_member_data(member_data)
        if errors:
            raise ValueError("\n".join(errors))
            
        if not member_data['member_number']:
            member_data['member_number'] = self.model.generate_unique_member_number()
            
        return member_data
    
    def update_button_states(self):
        """Update button enabled states based on selection"""
        has_selection = len(self.view.table.selectionModel().selectedRows()) > 0
        self.view.edit_button.setEnabled(has_selection)
        self.view.delete_button.setEnabled(has_selection)
        self.view.renew_button.setEnabled(has_selection)