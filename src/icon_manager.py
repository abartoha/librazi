from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

class IconManager:
    """Centralized icon management with fallback to generated icons"""
    
    def __init__(self):
        self.icon_cache = {}
        
    def get_icon(self, icon_name, color=None, size=16):
        """Get icon by name, with fallback to generated icon if file doesn't exist"""
        cache_key = f"{icon_name}_{color}_{size}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Try to load from file first
        file_path = f"assets/icon/{icon_name}.png"
        icon = QIcon(file_path)
        
        # If file doesn't exist or is null, create a fallback icon
        if icon.isNull():
            icon = self._create_fallback_icon(icon_name, color or "#555555", size)
        
        self.icon_cache[cache_key] = icon
        return icon
    
    def _create_fallback_icon(self, icon_name, color, size):
        """Create a simple fallback icon based on icon name"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(color))
        painter.setBrush(QColor(color))
        
        # Create different shapes based on icon name
        if icon_name == "add":
            self._draw_plus(painter, size)
        elif icon_name == "edit":
            self._draw_edit(painter, size)
        elif icon_name == "delete":
            self._draw_delete(painter, size)
        elif icon_name == "import":
            self._draw_import(painter, size)
        elif icon_name == "scan":
            self._draw_scan(painter, size)
        elif icon_name == "search":
            self._draw_search(painter, size)
        else:
            self._draw_default(painter, size)
        
        painter.end()
        return QIcon(pixmap)
    
    def _draw_plus(self, painter, size):
        """Draw a plus icon"""
        margin = size // 4
        painter.setPen(QColor("#4CAF50"))
        painter.setBrush(QColor("#4CAF50"))
        # Horizontal line
        painter.drawRect(margin, size//2 - 1, size - 2*margin, 2)
        # Vertical line
        painter.drawRect(size//2 - 1, margin, 2, size - 2*margin)
    
    def _draw_edit(self, painter, size):
        """Draw an edit/pencil icon"""
        painter.setPen(QColor("#2196F3"))
        painter.setBrush(QColor("#2196F3"))
        # Simple pencil shape
        points = [
            (size - 2, 2),
            (size - 6, 6),
            (4, size - 4),
            (2, size - 2),
            (size - 2, 2)
        ]
        painter.drawPolygon([painter.window().topLeft() + painter.window().bottomRight() * 0 for _ in points])
        # Simple diagonal line for pencil
        painter.drawLine(3, size - 3, size - 3, 3)
    
    def _draw_delete(self, painter, size):
        """Draw a delete/trash icon"""
        painter.setPen(QColor("#F44336"))
        painter.setBrush(QColor("#F44336"))
        # Trash can body
        margin = size // 4
        painter.drawRect(margin, margin + 2, size - 2*margin, size - margin - 4)
        # Trash can lid
        painter.drawRect(margin - 1, margin, size - 2*margin + 2, 2)
    
    def _draw_import(self, painter, size):
        """Draw an import/download icon"""
        painter.setPen(QColor("#FF9800"))
        painter.setBrush(QColor("#FF9800"))
        # Arrow pointing down
        center = size // 2
        margin = size // 4
        # Arrow shaft
        painter.drawRect(center - 1, margin, 2, size - 2*margin)
        # Arrow head
        painter.drawPolygon([
            painter.window().topLeft() + painter.window().bottomRight() * 0,
            painter.window().topLeft() + painter.window().bottomRight() * 0,
            painter.window().topLeft() + painter.window().bottomRight() * 0
        ])
    
    def _draw_scan(self, painter, size):
        """Draw a scan/QR code icon"""
        painter.setPen(QColor("#9C27B0"))
        painter.setBrush(QColor("#9C27B0"))
        # Simple grid pattern
        grid_size = 2
        for i in range(0, size, grid_size * 2):
            for j in range(0, size, grid_size * 2):
                if (i + j) % (grid_size * 4) == 0:
                    painter.drawRect(i, j, grid_size, grid_size)
    
    def _draw_search(self, painter, size):
        """Draw a search/magnifying glass icon"""
        painter.setPen(QColor("#607D8B"))
        painter.setBrush(Qt.NoBrush)
        # Circle
        margin = 2
        circle_size = size - 2*margin - 4
        painter.drawEllipse(margin, margin, circle_size, circle_size)
        # Handle
        painter.drawLine(size - margin - 2, size - margin - 2, size - margin, size - margin)
    
    def _draw_default(self, painter, size):
        """Draw a default icon"""
        painter.setPen(QColor("#757575"))
        painter.setBrush(QColor("#757575"))
        margin = size // 4
        painter.drawRect(margin, margin, size - 2*margin, size - 2*margin)

# Global icon manager instance
icon_manager = IconManager()