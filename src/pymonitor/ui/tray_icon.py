# src/pymonitor/ui/tray_icon.py

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication


class TrayIcon(QSystemTrayIcon):
    """Manages the system tray icon and its context menu using PyQt6."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        # Use a standard icon from the system's theme
        style = app.style()
        icon = style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
        self.setIcon(icon)
        self.setToolTip("PyMonitor.NET")

        # Create the context menu
        self.menu = QMenu()
        self.create_actions()
        self.setContextMenu(self.menu)

        self.activated.connect(self.on_activated)

    def create_actions(self):
        """Create the menu actions for the tray icon."""
        # Settings (Placeholder)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(settings_action)

        self.menu.addSeparator()

        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        self.menu.addAction(exit_action)

    def exit_application(self):
        """Safely exit the application."""
        print("Exit application requested from tray icon...")
        self.hide()  # Hide tray icon first

        # Force complete application termination
        self.app.exit()

        # As a last resort, force system exit
        import sys
        import os

        print("Forcing system exit...")
        os._exit(0)

    def show_settings(self):
        """Shows the settings window, ensuring it is brought to the front."""
        if self.app.settings_window.isHidden():
            self.app.settings_window.show()
        else:
            self.app.settings_window.activateWindow()
            self.app.settings_window.raise_()

    def on_activated(self, reason):
        """Handle activation events (e.g., clicks)."""
        # Show menu on left-click or right-click
        if reason in (self.ActivationReason.Trigger, self.ActivationReason.Context):
            self.contextMenu().popup(self.geometry().center())

    def run(self):
        """Shows the tray icon."""
        self.show()

    def stop(self):
        """Hides the tray icon."""
        self.hide()
