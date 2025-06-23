# src/pymonitor/main.py

import sys
from PyQt6.QtWidgets import QMessageBox
from .core.app import Application

def main():
    """Main entry point for the application."""
    try:
        app = Application(sys.argv)

        if app.is_already_running():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText("PyMonitor.NET is already running.")
            msg_box.setInformativeText("Another instance is already active. Please check the system tray.")
            msg_box.setWindowTitle("PyMonitor.NET - Instance Check")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            sys.exit(1)

        sys.exit(app.run())
    except Exception as e:
        # This will catch initialization errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
