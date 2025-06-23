# src/pymonitor/core/app.py

import sys
import time
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QSharedMemory

from ..hardware.monitor import HardwareMonitor
from ..config.settings import Settings
from ..ui.tray_icon import TrayIcon
from ..ui.watermark import WatermarkWindow
from ..ui.settings_window import SettingsWindow

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class HardwareWorker(QObject):
    """A worker that runs in a separate thread to fetch hardware data."""
    data_updated = pyqtSignal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.is_running = False

    def run(self):
        """The main work loop."""
        self.is_running = True
        while self.is_running:
            data = self.app.hardware_monitor.get_hardware_data()
            display_text = self.app._format_data_for_display(data)
            self.data_updated.emit(display_text)
            interval = self.app.settings.get('monitoring.update_interval', 2)
            time.sleep(interval)

    def stop(self):
        """Stops the worker loop."""
        self.is_running = False

class Application(QApplication):
    """Main application class, inheriting from QApplication for GUI support."""
    def __init__(self, args):
        super().__init__(args)

        # Single instance lock
        self.shared_memory = QSharedMemory("PyMonitor.NET_SINGLE_INSTANCE_LOCK")

        self.settings = Settings(os.path.join(PROJECT_ROOT, 'settings.json'))
        self.hardware_monitor = HardwareMonitor(self.settings, lib_path=PROJECT_ROOT)
        self.watermark = WatermarkWindow(self)
        self.tray_icon = TrayIcon(self)
        self.settings_window = SettingsWindow(self)

        self.setQuitOnLastWindowClosed(False)
        self.aboutToQuit.connect(self.cleanup)

    def is_already_running(self):
        """Checks if another instance of the application is running."""
        if self.shared_memory.attach():
            return True
        
        if self.shared_memory.create(1):
            return False
        else:
            print("Could not create shared memory segment.", file=sys.stderr)
            return True

    def run(self):
        """Initializes components and starts the application event loop."""
        print("Application starting...")
        self.hardware_monitor.initialize()

        # Set up the background thread for monitoring
        self.thread = QThread()
        self.worker = HardwareWorker(self)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.data_updated.connect(self.watermark.update_text)

        self.thread.start()
        self.watermark.show()
        self.tray_icon.run()
        
        print("Starting event loop...")
        return self.exec()

    def cleanup(self):
        """Clean up resources before exiting."""
        print("Application cleaning up...")
        if hasattr(self, 'worker') and self.worker.is_running:
            self.worker.stop()
        if hasattr(self, 'thread'):
            self.thread.quit()
            self.thread.wait()
        
        if self.shared_memory.isAttached():
            self.shared_memory.detach()
            
        print("Cleanup complete. Exiting.")

    def _format_data_for_display(self, data):
        """Formats the hardware data for display based on user settings."""
        lines = []
        enabled_sensors_config = self.settings.get('visualization.enabled_sensors', {})
        component_order = self.settings.get('visualization.component_order', [])
        show_titles = self.settings.get('visualization.show_component_titles', True)
        indentation = self.settings.get('visualization.sensor_indentation', 4)
        indent_space = "&nbsp;" * indentation
        category_spacing = self.settings.get('visualization.category_spacing', 1)
        display_mode = self.settings.get('visualization.display_mode', 'multiline')

        # Sort data based on the component_order setting
        if component_order:
            data.sort(key=lambda x: component_order.index(x['name']) if x['name'] in component_order else float('inf'))

        for hardware_item in data:
            hardware_name = hardware_item['name']
            enabled_sensors = enabled_sensors_config.get(hardware_name, [])
            
            filtered_sensors = [s for s in hardware_item['sensors'] if s['name'] in enabled_sensors]
            filtered_sensors.sort(key=lambda s: enabled_sensors.index(s['name']))

            if filtered_sensors:
                if display_mode == 'multiline':
                    if show_titles:
                        lines.append(f"<b>{hardware_name}</b>")
                    
                    for sensor in filtered_sensors:
                        prefix = indent_space if show_titles else ""
                        lines.append(f"{prefix}{sensor['name']}: {sensor['value']}")
                
                elif display_mode == 'singleline':
                    sensor_strings = [f"{s['name']}: {s['value']}" for s in filtered_sensors]
                    line = " | ".join(sensor_strings)
                    if show_titles:
                        lines.append(f"<b>{hardware_name}</b>: {line}")
                    else:
                        lines.append(line)

                # Add vertical spacing between categories
                for _ in range(category_spacing):
                    lines.append("")

        # Remove the last blank lines if they exist
        while lines and lines[-1] == "":
            lines.pop()

        return "<br>".join(lines)

    def cleanup(self):
        """Performs cleanup operations before exiting."""
        print("Cleaning up resources...")
        self.worker.stop()
        self.thread.quit()
        self.thread.wait() # Wait for the thread to finish
        self.hardware_monitor.close()
        print("Application stopped.")

    def exit(self):
        """Signals the application to exit gracefully."""
        print("Exit requested.")
        self.quit()
