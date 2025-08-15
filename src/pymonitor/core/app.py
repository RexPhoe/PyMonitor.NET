# src/pymonitor/core/app.py

import sys
import time
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QSharedMemory
from PyQt6.QtGui import QFontDatabase

from ..hardware.monitor import HardwareMonitor
from ..config.settings import Settings
from ..ui.tray_icon import TrayIcon
from ..ui.watermark import WatermarkWindow
from ..ui.settings_window import SettingsWindow

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)


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
            interval = self.app.settings.get("monitoring.update_interval", 2)
            time.sleep(interval)

    def stop(self):
        """Stops the worker loop."""
        self.is_running = False


class Application(QApplication):
    """Main application class, inheriting from QApplication for GUI support."""

    def __init__(self, args):
        super().__init__(args)

        # Load bundled Nerd Fonts so icons render even if not installed system-wide
        try:
            fonts_dir = os.path.join(PROJECT_ROOT, "fonts")
            if os.path.isdir(fonts_dir):
                for fname in os.listdir(fonts_dir):
                    if fname.lower().endswith(".ttf"):
                        QFontDatabase.addApplicationFont(os.path.join(fonts_dir, fname))
        except Exception as e:
            # Non-fatal: continue even if fonts fail to load
            print(f"Warning: failed to load fonts: {e}")

        # Single instance lock
        self.shared_memory = QSharedMemory("PyMonitor.NET_SINGLE_INSTANCE_LOCK")

        self.settings = Settings(os.path.join(PROJECT_ROOT, "settings.json"))
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
        try:
            # Stop the worker thread
            if hasattr(self, "worker") and self.worker:
                print("Stopping worker...")
                self.worker.stop()

            # Stop and wait for thread to finish
            if hasattr(self, "thread") and self.thread:
                print("Stopping thread...")
                self.thread.quit()
                self.thread.wait(3000)  # Wait max 3 seconds for thread to finish

            # Close hardware monitor
            if hasattr(self, "hardware_monitor") and self.hardware_monitor:
                print("Closing hardware monitor...")
                self.hardware_monitor.close()

            # Hide tray icon
            if hasattr(self, "tray_icon") and self.tray_icon:
                print("Hiding tray icon...")
                self.tray_icon.hide()

            # Hide watermark window
            if hasattr(self, "watermark") and self.watermark:
                print("Hiding watermark...")
                self.watermark.hide()

            # Close settings window
            if hasattr(self, "settings_window") and self.settings_window:
                print("Closing settings window...")
                self.settings_window.close()

            # Detach shared memory
            if hasattr(self, "shared_memory") and self.shared_memory.isAttached():
                print("Detaching shared memory...")
                self.shared_memory.detach()

        except Exception as e:
            print(f"Error during cleanup: {e}")

        print("Cleanup complete. Exiting.")

    def exit(self):
        """Signals the application to exit gracefully."""
        print("Exit requested.")
        # Only perform cleanup manually if we're actually exiting via tray
        # Don't call cleanup here to avoid interference with normal startup
        self.quit()

    def _format_data_for_display(self, data):
        """Formats the hardware data for display based on user settings."""
        lines = []
        enabled_sensors_config = self.settings.get("visualization.enabled_sensors", {})
        component_order = self.settings.get("visualization.component_order", [])
        show_titles = self.settings.get("visualization.show_component_titles", True)
        indentation = self.settings.get("visualization.sensor_indentation", 4)
        indent_space = "&nbsp;" * indentation
        category_spacing = self.settings.get("visualization.category_spacing", 1)
        display_mode = self.settings.get("visualization.display_mode", "multiline")
        show_icons = self.settings.get("visualization.show_icons", True)

        # Read customizable icons from settings with fallback defaults
        icons_cfg = self.settings.get("icons", {}) or {}
        hw_icons_user = icons_cfg.get("hardware", {}) or {}
        sensor_icons_user = icons_cfg.get("sensors", {}) or {}

        hw_icons_fallback = {
            "Cpu": "\uf2db",
            "GPU": "\uf21b5",
            "GpuNvidia": "\uf21b5",
            "GpuAmd": "\uf21b5",
            "GpuIntel": "\uf21b5",
            "Memory": "\uf96a",
            "Motherboard": "\uf2db",
            "Storage": "\uf287",
            "HDD": "\uf287",
            "SSD": "\uf287",
            "Network": "\uf6ff",
            "Wifi": "\uf5a9",
        }
        sensor_icons_fallback = {
            "temperature": "\uf2c9",
            "load": "\uf141",
            "clock": "\uf251",
            "power": "\uf0e7",
            "fan": "\uf863",
            "data": "\uf1c0",
            "voltage": "\uf1e6",
        }

        def get_hw_icon(hw_type_or_name: str) -> str:
            if not hw_type_or_name:
                return ""
            # Exact user overrides first
            if hw_type_or_name in hw_icons_user:
                return hw_icons_user[hw_type_or_name]
            cap = hw_type_or_name.capitalize()
            if cap in hw_icons_user:
                return hw_icons_user[cap]
            # Fallback exacts
            if hw_type_or_name in hw_icons_fallback:
                return hw_icons_fallback[hw_type_or_name]
            if cap in hw_icons_fallback:
                return hw_icons_fallback[cap]
            # Heuristics by substring
            low = hw_type_or_name.lower()
            if "gpu" in low:
                return hw_icons_user.get("GPU", hw_icons_fallback.get("GPU", ""))
            if "cpu" in low:
                return hw_icons_user.get("Cpu", hw_icons_fallback.get("Cpu", ""))
            if "mem" in low:
                return hw_icons_user.get("Memory", hw_icons_fallback.get("Memory", ""))
            if "stor" in low or "disk" in low:
                return hw_icons_user.get(
                    "Storage", hw_icons_fallback.get("Storage", "")
                )
            if "net" in low:
                return hw_icons_user.get(
                    "Network", hw_icons_fallback.get("Network", "")
                )
            if "wifi" in low:
                return hw_icons_user.get("Wifi", hw_icons_fallback.get("Wifi", ""))
            return ""

        def get_sensor_icon_by_type(sensor_type_str: str) -> str:
            t = (sensor_type_str or "").lower()
            if "temperature" in t:
                return sensor_icons_user.get(
                    "temperature", sensor_icons_fallback["temperature"]
                )
            if "load" in t:
                return sensor_icons_user.get("load", sensor_icons_fallback["load"])
            if "clock" in t:
                return sensor_icons_user.get("clock", sensor_icons_fallback["clock"])
            if "power" in t:
                return sensor_icons_user.get("power", sensor_icons_fallback["power"])
            if "fan" in t:
                return sensor_icons_user.get("fan", sensor_icons_fallback["fan"])
            if "data" in t:
                return sensor_icons_user.get("data", sensor_icons_fallback["data"])
            if "voltage" in t:
                return sensor_icons_user.get(
                    "voltage", sensor_icons_fallback["voltage"]
                )
            return ""

        # Sort data based on the component_order setting
        if component_order:
            data.sort(
                key=lambda x: (
                    component_order.index(x["name"])
                    if x["name"] in component_order
                    else float("inf")
                )
            )

        section_count = 0  # Track number of sections added
        
        for hardware_item in data:
            hardware_name = hardware_item["name"]
            hardware_type = hardware_item.get("type", "")
            enabled_sensors = enabled_sensors_config.get(hardware_name, [])

            filtered_sensors = [
                s for s in hardware_item["sensors"] if s["name"] in enabled_sensors
            ]
            filtered_sensors.sort(key=lambda s: enabled_sensors.index(s["name"]))

            if filtered_sensors:
                # Add spacing before this section (but not before the first section)
                if section_count > 0 and category_spacing > 0:
                    lines.append(
                        f'<div style="margin-bottom: {category_spacing}px;"></div>'
                    )
                title_icon = (
                    get_hw_icon(hardware_type or hardware_name) if show_icons else ""
                )
                title_prefix = (title_icon + " ") if (show_icons and title_icon) else ""

                if display_mode == "multiline":
                    if show_titles:
                        lines.append(f"<b>{title_prefix}{hardware_name}</b>")

                    for sensor in filtered_sensors:
                        prefix = indent_space if show_titles else ""
                        sensor_icon = (
                            get_sensor_icon_by_type(sensor.get("type", ""))
                            if show_icons
                            else ""
                        )
                        sensor_label = (
                            f"{sensor_icon} {sensor['name']}"
                            if sensor_icon
                            else sensor["name"]
                        )
                        lines.append(f"{prefix}{sensor_label}: {sensor['value']}")
                elif display_mode == "singleline":
                    sensor_strings = []
                    for s in filtered_sensors:
                        sensor_icon = (
                            get_sensor_icon_by_type(s.get("type", ""))
                            if show_icons
                            else ""
                        )
                        name_part = (
                            f"{sensor_icon} {s['name']}" if sensor_icon else s["name"]
                        )
                        sensor_strings.append(f"{name_part}: {s['value']}")
                    line = " | ".join(sensor_strings)
                    if show_titles:
                        lines.append(f"<b>{title_prefix}{hardware_name}</b>: {line}")
                    else:
                        lines.append(line)

                # Increment section counter since we added a section
                section_count += 1

        # Remove the last blank lines if they exist
        while lines and lines[-1] == "":
            lines.pop()

        return "<br>".join(lines)
