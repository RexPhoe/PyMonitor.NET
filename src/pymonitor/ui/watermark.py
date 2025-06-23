# src/pymonitor/ui/watermark.py

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot

class WatermarkWindow(QWidget):
    """Displays the hardware data as a transparent, click-through overlay using PyQt6."""
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = app.settings

        # Base flags for a frameless, non-interactive overlay
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool | # Hides the window from the taskbar
            Qt.WindowType.WindowTransparentForInput # Makes the window click-through
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout and label to display the text
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Initializing...")
        self.label.setWordWrap(True) # Enable word wrap for alignment
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Initial setup from settings
        self.update_appearance()
        self.update_flags()

    @pyqtSlot(str)
    def update_text(self, text):
        """Updates the text and triggers a style/size/position refresh."""
        self.label.setText(text)
        # Appearance update will handle resizing and repositioning
        self.update_appearance()

    def update_position(self):
        """Calculates and sets the window position. Should be called after resizing."""
        monitor_index = self.settings.get('position.monitor', 0)
        screens = QApplication.screens()
        if monitor_index >= len(screens):
            monitor_index = 0 # Default to primary screen
        screen_geometry = screens[monitor_index].geometry()

        anchor = self.settings.get('position.anchor', 'top_left')
        offset_x = self.settings.get('position.offset_x', 10)
        offset_y = self.settings.get('position.offset_y', 10)

        win_size = self.size() # Use current, fixed size

        # Horizontal alignment
        if 'left' in anchor:
            x = screen_geometry.x() + offset_x
        elif 'center' in anchor:
            x = screen_geometry.x() + (screen_geometry.width() - win_size.width()) // 2 + offset_x
        elif 'right' in anchor:
            x = screen_geometry.x() + screen_geometry.width() - win_size.width() - offset_x
        else:
            x = screen_geometry.x() + offset_x # Default case

        # Vertical alignment
        if 'top' in anchor:
            y = screen_geometry.y() + offset_y
        elif 'middle' in anchor:
            y = screen_geometry.y() + (screen_geometry.height() - win_size.height()) // 2 + offset_y
        elif 'bottom' in anchor:
            y = screen_geometry.y() + screen_geometry.height() - win_size.height() - offset_y
        else:
            y = screen_geometry.y() + offset_y # Default case

        self.move(x, y)

    def update_flags(self):
        """Updates window flags like 'always on top'."""
        always_on_top = self.settings.get('window.always_on_top', True)
        current_flags = self.windowFlags()
        
        if always_on_top:
            if not (current_flags & Qt.WindowType.WindowStaysOnTopHint):
                self.setWindowFlags(current_flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            if current_flags & Qt.WindowType.WindowStaysOnTopHint:
                self.setWindowFlags(current_flags & ~Qt.WindowType.WindowStaysOnTopHint)
        
        # This is crucial to apply flag changes to an already visible window
        self.show()

    def update_appearance(self):
        """Updates style, resizes, and repositions the window based on settings."""
        # Get all appearance and position settings needed for styling and sizing
        font_family = self.settings.get('appearance.font_family', 'Arial')
        font_size = int(self.settings.get('appearance.font_size', 12))
        color = self.settings.get('appearance.font_color', '#FFFFFF')
        opacity = self.settings.get('appearance.opacity', 100)
        align_str = self.settings.get('appearance.text_align', 'left')
        width = int(self.settings.get('position.width', 400))

        # Apply font and color via stylesheet for robustness
        self.label.setStyleSheet(f"""
            QLabel {{
                font-family: '{font_family}';
                font-size: {font_size}pt;
                color: {color};
            }}
        """)

        # Set Text Alignment
        if align_str == 'center':
            alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        elif align_str == 'right':
            alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        else:  # 'left'
            alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        self.label.setAlignment(alignment)

        # Set fixed width and calculate required height
        self.setFixedWidth(width)
        # Calculate height based on the label's content and new width
        height = self.label.heightForWidth(width)
        self.setFixedHeight(height)

        # Apply opacity to the whole window
        self.setWindowOpacity(opacity / 100.0)

        # Finally, update the position since the size might have changed
        self.update_position()

    def closeEvent(self, event):
        """Ensure the application doesn't exit when this window is closed."""
        # This window should not be closable by the user, but as a safeguard:
        event.ignore()


    def closeEvent(self, event):
        """Ensure the application doesn't exit when this window is closed."""
        # This window should not be closable by the user, but as a safeguard:
        event.ignore()
        self.update_position()

    def closeEvent(self, event):
        """Handle the close event."""
        self.app.exit()
        event.accept()
