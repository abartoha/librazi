from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QDialog, 
                             QFormLayout, QComboBox, QSpinBox, QLabel, QToolButton, 
                             QDateEdit, QFrame, QHeaderView, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, timedelta
from icon_manager import icon_manager
import os
from PyQt5.QtCore import QFile, QTextStream

class StyledButton(QPushButton):
    """Custom styled button with hover effects"""
    def __init__(self, text, icon_name=None, primary=False):
        super().__init__(text)
        if icon_name:
            try:
                self.setIcon(icon_manager.get_icon(icon_name))
            except:
                pass  # No icon if manager fails
        self.primary = primary
        self.setProperty("primary", str(primary).lower())

class StyledToolButton(QToolButton):
    """Custom styled tool button"""
    def __init__(self, icon_name, tooltip="", button_type="default"):
        super().__init__()
        self.setIcon(icon_manager.get_icon(icon_name))
        self.setToolTip(tooltip)
        self.setProperty("button_type", button_type)

class SearchFrame(QFrame):
    """Styled search and filter frame"""
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setObjectName("searchFrame")
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(12)

class MemberManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        """Load styles from external CSS file"""
        css_file = QFile("assets/css/styles.css")
        if css_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(css_file)
            self.setStyleSheet(stream.readAll())
            css_file.close()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("👥 Member Management")
        title_label.setObjectName("titleLabel")
        
        # Search and filter frame
        search_frame = SearchFrame()
        
        # Search and filter widgets
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, email, member number, or phone...")
        self.search_input.setMinimumHeight(40)
        
        self.membership_status_filter = QComboBox()
        self.membership_status_filter.addItems(['All', 'Active', 'Expired', 'Suspended', 'Cancelled'])
        self.membership_status_filter.setMinimumHeight(40)
        
        self.membership_type_filter = QComboBox()
        self.membership_type_filter.addItems(['All', 'Regular', 'Student', 'Senior', 'Premium'])
        self.membership_type_filter.setMinimumHeight(40)
        
        self.search_button = StyledButton("Search", "search", primary=True)
        self.clear_search_button = StyledButton("Clear", "delete")
        
        # Add widgets to search frame layout
        search_frame.layout().addWidget(QLabel("Search:"))
        search_frame.layout().addWidget(self.search_input, 2)
        search_frame.layout().addWidget(QLabel("Status:"))
        search_frame.layout().addWidget(self.membership_status_filter)
        search_frame.layout().addWidget(QLabel("Type:"))
        search_frame.layout().addWidget(self.membership_type_filter)
        search_frame.layout().addWidget(self.search_button)
        search_frame.layout().addWidget(self.clear_search_button)
        
        # Member Table
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Member #", "Name", "Email", "Phone", "Status", 
            "Join Date", "Expiry Date", "Books Loaned", "Total Fines", "Last Activity", "Actions"
        ])
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        # Column setup
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        
        # Set initial column widths
        column_widths = [60, 100, 180, 200, 120, 100, 100, 100, 80, 80, 100, 140]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        
        # Set resize modes
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Member #
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Phone
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Status
        header.setSectionResizeMode(6, QHeaderView.Interactive)  # Join Date
        header.setSectionResizeMode(7, QHeaderView.Interactive)  # Expiry Date
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Books Loaned
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # Total Fines
        header.setSectionResizeMode(10, QHeaderView.Interactive)  # Last Activity
        header.setSectionResizeMode(11, QHeaderView.Fixed)  # Actions
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.add_button = StyledButton("➕ Add Member", "add", primary=True)
        self.add_button.setShortcut('Ctrl+A')
        self.add_button.setMinimumHeight(45)
        
        self.edit_button = StyledButton("✏️ Edit Member", "edit")
        self.edit_button.setShortcut('Ctrl+E')
        self.edit_button.setMinimumHeight(45)
        
        self.delete_button = StyledButton("🗑️ Delete Member", "delete")
        self.delete_button.setShortcut('Ctrl+D')
        self.delete_button.setMinimumHeight(45)
        
        self.renew_button = StyledButton("🔄 Renew Membership", "import")
        self.renew_button.setMinimumHeight(45)
        
        self.import_button = StyledButton("📥 Import Members", "import")
        self.import_button.setMinimumHeight(45)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.renew_button)
        button_layout.addWidget(self.import_button)
        button_layout.addStretch()
        
        button_frame.setLayout(button_layout)
        
        # Add all components to main layout
        self.layout.addWidget(title_label)
        self.layout.addWidget(search_frame)
        self.layout.addWidget(self.table, 1)
        self.layout.addWidget(button_frame)
        
        self.setLayout(self.layout)

    def resize_columns(self):
        """Enhanced column resizing with better proportions"""
        header = self.table.horizontalHeader()
        
        # Get total available width
        total_width = self.table.viewport().width()
        
        # Reserve space for fixed columns
        fixed_width = 60 + 80 + 80 + 140  # ID + Books Loaned + Total Fines + Actions
        available_width = total_width - fixed_width
        
        # Distribute remaining width proportionally
        if available_width > 0:
            member_num_width = int(available_width * 0.1)
            name_width = int(available_width * 0.25)
            email_width = int(available_width * 0.3)
            phone_width = int(available_width * 0.15)
            status_width = int(available_width * 0.1)
            date_width = int(available_width * 0.05)  # Split between join/expiry
            
            self.table.setColumnWidth(1, max(member_num_width, 100))
            self.table.setColumnWidth(2, max(name_width, 150))
            self.table.setColumnWidth(3, max(email_width, 180))
            self.table.setColumnWidth(4, max(phone_width, 120))
            self.table.setColumnWidth(5, max(status_width, 100))
            self.table.setColumnWidth(6, max(date_width, 90))
            self.table.setColumnWidth(7, max(date_width, 90))
            self.table.setColumnWidth(10, max(date_width, 90))

    def show_members(self, members):
        """Enhanced member display with better formatting and styling"""
        self.table.clearContents()
        self.table.setRowCount(len(members))
        current_date = datetime.now().date()
        
        for row_idx, row in enumerate(members):
            # Set row height for better appearance
            self.table.setRowHeight(row_idx, 50)
            
            # Display member data with enhanced formatting
            for col_idx, value in enumerate(row[:11]):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Special formatting for specific columns
                if col_idx == 2:  # Name column - combine first and last name if separate
                    if isinstance(value, tuple) and len(value) >= 2:
                        item.setText(f"{value[0]} {value[1]}")
                elif col_idx == 5:  # Status column
                    status = str(value).lower() if value else "unknown"
                    if status == 'active':
                        item.setBackground(QColor("#E8F5E8"))  # Light green
                        item.setForeground(QColor("#2E7D32"))  # Dark green
                    elif status == 'expired':
                        item.setBackground(QColor("#FFF3E0"))  # Light orange
                        item.setForeground(QColor("#F57C00"))  # Orange
                    elif status in ['suspended', 'cancelled']:
                        item.setBackground(QColor("#FFEBEE"))  # Light red
                        item.setForeground(QColor("#C62828"))  # Red
                elif col_idx in [6, 7, 10]:  # Date columns
                    if value:
                        try:
                            # Format date consistently
                            if isinstance(value, str):
                                date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                            else:
                                date_obj = value
                            item.setText(date_obj.strftime('%Y-%m-%d'))
                            
                            # Highlight expiry dates
                            if col_idx == 7:  # Expiry date
                                days_until_expiry = (date_obj - current_date).days
                                if days_until_expiry < 0:
                                    item.setBackground(QColor("#FFEBEE"))  # Expired - red
                                elif days_until_expiry <= 30:
                                    item.setBackground(QColor("#FFF3E0"))  # Expiring soon - orange
                        except (ValueError, TypeError):
                            item.setText(str(value) if value else "")
                elif col_idx in [8, 9]:  # Numeric columns (Books Loaned, Total Fines)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    if col_idx == 9:  # Total Fines
                        try:
                            fine_amount = float(value) if value else 0.0
                            if fine_amount > 0:
                                item.setForeground(QColor("#D32F2F"))  # Red for outstanding fines
                                item.setText(f"${fine_amount:.2f}")
                            else:
                                item.setText("$0.00")
                        except (ValueError, TypeError):
                            item.setText("$0.00")
                
                self.table.setItem(row_idx, col_idx, item)
            
            # Enhanced action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(4, 4, 4, 4)
            action_layout.setSpacing(4)
            
            member_id = str(row[0])
            edit_btn = StyledToolButton("edit", "Edit Member", "edit")
            edit_btn.setProperty('member_id', member_id)
            
            delete_btn = StyledToolButton("delete", "Delete Member", "delete")
            delete_btn.setProperty('member_id', member_id)
            
            renew_btn = StyledToolButton("import", "Renew Membership", "renew")
            renew_btn.setProperty('member_id', member_id)
            
            view_loans_btn = StyledToolButton("search", "View Loans", "view")
            view_loans_btn.setProperty('member_id', member_id)
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(renew_btn)
            action_layout.addWidget(view_loans_btn)
            action_layout.addStretch()
            
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 11, action_widget)
        
        self.resize_columns()

    def show_error(self, message):
        """Enhanced error dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("❌ Error")
        msg.setText(message)
        msg.setObjectName("errorDialog")
        msg.exec_()

    def show_success(self, message):
        """Success dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("✅ Success")
        msg.setText(message)
        msg.setObjectName("successDialog")
        msg.exec_()

    def show_member_dialog(self, member_data=None):
        """Enhanced member dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Edit Member" if member_data else "➕ Add New Member")
        dialog.setModal(True)
        dialog.resize(600, 700)
        dialog.setObjectName("memberDialog")
        
        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Personal Information Section
        personal_label = QLabel("👤 Personal Information")
        personal_label.setObjectName("sectionLabel")
        layout.addRow(personal_label)
        
        # Form fields
        member_number = QLineEdit(member_data.get('member_number', '') if member_data else '')
        member_number.setPlaceholderText("Auto-generated if left empty")
        if member_data:
            member_number.setReadOnly(True)  # Don't allow editing existing member numbers
        
        first_name = QLineEdit(member_data.get('first_name', '') if member_data else '')
        first_name.setPlaceholderText("Enter first name...")
        
        last_name = QLineEdit(member_data.get('last_name', '') if member_data else '')
        last_name.setPlaceholderText("Enter last name...")
        
        email = QLineEdit(member_data.get('email', '') if member_data else '')
        email.setPlaceholderText("Enter email address...")
        
        phone = QLineEdit(member_data.get('phone', '') if member_data else '')
        phone.setPlaceholderText("Enter phone number...")
        
        date_of_birth = QDateEdit()
        date_of_birth.setCalendarPopup(True)
        date_of_birth.setMaximumDate(QDate.currentDate().addYears(-1))
        date_of_birth.setMinimumDate(QDate(1900, 1, 1))
        if member_data and member_data.get('date_of_birth'):
            if isinstance(member_data['date_of_birth'], str):
                date_of_birth.setDate(QDate.fromString(member_data['date_of_birth'], 'yyyy-MM-dd'))
            else:
                date_of_birth.setDate(member_data['date_of_birth'])
        else:
            date_of_birth.setDate(QDate.currentDate().addYears(-18))
        
        # Address
        address = QTextEdit(member_data.get('address', '') if member_data else '')
        address.setPlaceholderText("Enter full address...")
        address.setMaximumHeight(80)
        
        # Membership Information Section
        membership_label = QLabel("📋 Membership Information")
        membership_label.setObjectName("sectionLabel")
        layout.addRow(membership_label)
        
        membership_date = QDateEdit()
        membership_date.setCalendarPopup(True)
        membership_date.setMaximumDate(QDate.currentDate())
        if member_data and member_data.get('membership_date'):
            if isinstance(member_data['membership_date'], str):
                membership_date.setDate(QDate.fromString(member_data['membership_date'], 'yyyy-MM-dd'))
            else:
                membership_date.setDate(member_data['membership_date'])
        else:
            membership_date.setDate(QDate.currentDate())
        
        membership_expiry = QDateEdit()
        membership_expiry.setCalendarPopup(True)
        membership_expiry.setMinimumDate(QDate.currentDate())
        if member_data and member_data.get('membership_expiry'):
            if isinstance(member_data['membership_expiry'], str):
                membership_expiry.setDate(QDate.fromString(member_data['membership_expiry'], 'yyyy-MM-dd'))
            else:
                membership_expiry.setDate(member_data['membership_expiry'])
        else:
            membership_expiry.setDate(QDate.currentDate().addYears(1))
        
        membership_status = QComboBox()
        membership_status.addItems(['active', 'expired', 'suspended', 'cancelled'])
        if member_data and member_data.get('membership_status'):
            membership_status.setCurrentText(member_data['membership_status'])
        
        max_books_allowed = QSpinBox()
        max_books_allowed.setRange(1, 20)
        max_books_allowed.setValue(member_data.get('max_books_allowed', 5) if member_data else 5)
        
        max_renewal_allowed = QSpinBox()
        max_renewal_allowed.setRange(0, 10)
        max_renewal_allowed.setValue(member_data.get('max_renewal_allowed', 2) if member_data else 2)
        
        # Emergency Contact Section
        emergency_label = QLabel("🚨 Emergency Contact")
        emergency_label.setObjectName("sectionLabel")
        layout.addRow(emergency_label)
        
        emergency_contact_name = QLineEdit(member_data.get('emergency_contact_name', '') if member_data else '')
        emergency_contact_name.setPlaceholderText("Enter emergency contact name...")
        
        emergency_contact_phone = QLineEdit(member_data.get('emergency_contact_phone', '') if member_data else '')
        emergency_contact_phone.setPlaceholderText("Enter emergency contact phone...")
        
        # Notes
        member_notes = QTextEdit(member_data.get('member_notes', '') if member_data else '')
        member_notes.setPlaceholderText("Add any notes about this member...")
        member_notes.setMaximumHeight(80)
        
        # Add form rows
        layout.addRow("🏷️ Member Number:", member_number)
        layout.addRow("👤 First Name:", first_name)
        layout.addRow("👤 Last Name:", last_name)
        layout.addRow("📧 Email:", email)
        layout.addRow("📞 Phone:", phone)
        layout.addRow("🎂 Date of Birth:", date_of_birth)
        layout.addRow("🏠 Address:", address)
        
        layout.addRow(membership_label)
        layout.addRow("📅 Join Date:", membership_date)
        layout.addRow("⏰ Expiry Date:", membership_expiry)
        layout.addRow("📊 Status:", membership_status)
        layout.addRow("📚 Max Books:", max_books_allowed)
        layout.addRow("🔄 Max Renewals:", max_renewal_allowed)
        
        layout.addRow(emergency_label)
        layout.addRow("👤 Contact Name:", emergency_contact_name)
        layout.addRow("📞 Contact Phone:", emergency_contact_phone)
        
        layout.addRow("📝 Notes:", member_notes)
        
        # Buttons
        save_button = StyledButton("💾 Save Member", primary=True)
        save_button.setMinimumHeight(40)
        
        cancel_button = StyledButton("❌ Cancel")
        cancel_button.setMinimumHeight(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addRow(button_layout)
        dialog.setLayout(layout)
        
        return dialog, {
            'member_number': member_number,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'date_of_birth': date_of_birth,
            'address': address,
            'membership_date': membership_date,
            'membership_expiry': membership_expiry,
            'membership_status': membership_status,
            'max_books_allowed': max_books_allowed,
            'max_renewal_allowed': max_renewal_allowed,
            'emergency_contact_name': emergency_contact_name,
            'emergency_contact_phone': emergency_contact_phone,
            'member_notes': member_notes,
            'save_button': save_button,
            'cancel_button': cancel_button
        }

    def show_member_loans_dialog(self, member_id, member_name, loans):
        """Show dialog with member's loan history"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📚 Loan History for {member_name}")
        dialog.resize(800, 600)
        dialog.setModal(True)
        dialog.setObjectName("loansDialog")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(f"📚 Loan History for: {member_name}")
        title_label.setObjectName("titleLabel")
        
        # Loans Table
        loans_table = QTableWidget()
        loans_table.setColumnCount(7)
        loans_table.setHorizontalHeaderLabels([
            "Loan ID", "Book Title", "Loan Date", "Due Date", "Return Date", "Status", "Renewals"
        ])
        loans_table.setSelectionMode(QTableWidget.SingleSelection)
        loans_table.setSelectionBehavior(QTableWidget.SelectRows)
        loans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        loans_table.setAlternatingRowColors(True)
        loans_table.verticalHeader().setVisible(False)
        loans_table.setMinimumHeight(400)
        
        # Populate loans table
        loans_table.setRowCount(len(loans))
        for row_idx, loan in enumerate(loans):
            for col_idx, value in enumerate(loan):
                item = QTableWidgetItem(str(value) if value else "")
                
                # Color code based on status
                if col_idx == 5:  # Status column
                    status = str(value).lower() if value else "unknown"
                    if status == 'active':
                        item.setBackground(QColor("#FFF3E0"))  # Light orange
                    elif status == 'returned':
                        item.setBackground(QColor("#E8F5E8"))  # Light green
                    elif status == 'overdue':
                        item.setBackground(QColor("#FFEBEE"))  # Light red
                
                loans_table.setItem(row_idx, col_idx, item)
        
        # Resize columns
        loans_table.resizeColumnsToContents()
        
        # Close button
        close_button = StyledButton("❌ Close")
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(dialog.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addWidget(title_label)
        layout.addWidget(loans_table, 1)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        return dialog

    def show_renewal_dialog(self, member_id, member_name, current_expiry):
        """Show membership renewal dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"🔄 Renew Membership for {member_name}")
        dialog.setModal(True)
        dialog.resize(400, 300)
        dialog.setObjectName("renewalDialog")
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Current expiry info
        current_expiry_label = QLabel(f"Current Expiry: {current_expiry}")
        current_expiry_label.setObjectName("infoLabel")
        
        # New expiry date
        new_expiry = QDateEdit()
        new_expiry.setCalendarPopup(True)
        new_expiry.setMinimumDate(QDate.currentDate())
        new_expiry.setDate(QDate.currentDate().addYears(1))
        
        # Renewal period options
        renewal_period = QComboBox()
        renewal_period.addItems(['1 Year', '6 Months', '3 Months', 'Custom'])
        
        def update_expiry_date():
            period = renewal_period.currentText()
            base_date = QDate.currentDate()
            if period == '1 Year':
                new_expiry.setDate(base_date.addYears(1))
            elif period == '6 Months':
                new_expiry.setDate(base_date.addMonths(6))
            elif period == '3 Months':
                new_expiry.setDate(base_date.addMonths(3))
            # Custom allows manual date selection
        
        renewal_period.currentTextChanged.connect(update_expiry_date)
        
        # Form layout
        layout.addRow(current_expiry_label)
        layout.addRow("🔄 Renewal Period:", renewal_period)
        layout.addRow("📅 New Expiry Date:", new_expiry)
        
        # Buttons
        renew_button = StyledButton("✅ Renew Membership", primary=True)
        renew_button.setMinimumHeight(40)
        
        cancel_button = StyledButton("❌ Cancel")
        cancel_button.setMinimumHeight(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(renew_button)
        
        layout.addRow(button_layout)
        dialog.setLayout(layout)
        
        return dialog, {
            'new_expiry': new_expiry,
            'renewal_period': renewal_period,
            'renew_button': renew_button,
            'cancel_button': cancel_button
        }