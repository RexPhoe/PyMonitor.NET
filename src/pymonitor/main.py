# src/pymonitor/main.py

import sys
from PyQt6.QtWidgets import QMessageBox
from .core.app import Application
from .hardware.monitor import UntrustedLocationError

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
    except UntrustedLocationError as e:
        # Handle the specific case of untrusted location
        print("=" * 60)
        print("🚫 UNTRUSTED LOCATION ERROR")
        print("=" * 60)
        print(str(e))
        print("=" * 60)
        
        # Also show GUI message if possible
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setText("Cannot load from untrusted location")
            msg_box.setInformativeText(
                "The application is in a location that .NET considers untrusted "
                "(like Downloads folder).\n\n"
                "Please move the entire PyMonitor.NET folder to a trusted location like:\n"
                "• C:\\Program Files\\PyMonitor.NET\n"
                "• C:\\Users\\YourUser\\Documents\\PyMonitor.NET\n"
                "• C:\\PyMonitor.NET\n\n"
                "Then run the application from the new location."
            )
            msg_box.setWindowTitle("PyMonitor.NET - Security Error")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        except:
            pass  # If GUI fails, at least we printed the console message
        
        sys.exit(1)
    except Exception as e:
        # This will catch other initialization errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        
        # Show additional help for common issues
        error_str = str(e).lower()
        if "librehardwaremonitorlib" in error_str:
            print("\n💡 Possible solutions:")
            print("1. Make sure LibreHardwareMonitorLib.dll is in the same folder as the application")
            print("2. If the file is there, try moving the entire folder to a different location")
            print("3. Right-click on LibreHardwareMonitorLib.dll → Properties → Unblock")
            print("4. Run as Administrator if necessary")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
