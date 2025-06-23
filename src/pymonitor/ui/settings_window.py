# src/pymonitor/ui/settings_window.py

from PyQt6.QtWidgets import (
    QApplication, QDialog, QTabWidget, QVBoxLayout, QWidget, QFormLayout, QComboBox,
    QFontComboBox, QSpinBox, QPushButton, QColorDialog, 
    QCheckBox, QDialogButtonBox, QLabel, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QSlider, QHBoxLayout
)
import copy
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ..core.version_checker import get_latest_lhm_version

class SettingsWindow(QDialog):
    """The main settings window for the application."""
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = app.settings
        self.original_settings = None


        self.setWindowTitle("PyMonitor.NET Settings")
        self.setMinimumSize(500, 400)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create tabs
        self.create_position_tab()
        self.create_appearance_tab()
        self.create_visualization_tab()
        self.create_about_tab()
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def showEvent(self, event):
        """Called when the dialog is shown. We capture the original settings here."""
        self.original_settings = copy.deepcopy(self.settings.data)
        self.populate_sensor_tree() # Ensure the list is fresh every time
        super().showEvent(event)

    def create_position_tab(self):
        """Creates the Position settings tab."""
        tab = QWidget()
        layout = QFormLayout()

        # Monitor Selection
        self.monitor_combo = QComboBox()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            self.monitor_combo.addItem(f"Monitor {i+1}: {screen.size().width()}x{screen.size().height()}", i)
        current_monitor = self.settings.get('position.monitor', 0)
        self.monitor_combo.setCurrentIndex(current_monitor)
        self.monitor_combo.currentIndexChanged.connect(self.update_monitor)
        layout.addRow("Display Monitor:", self.monitor_combo)

        # Anchor Point
        self.anchor_combo = QComboBox()
        anchors = {
            'Top Left': 'top_left', 'Top Center': 'top_center', 'Top Right': 'top_right',
            'Middle Left': 'middle_left', 'Center': 'center', 'Middle Right': 'middle_right',
            'Bottom Left': 'bottom_left', 'Bottom Center': 'bottom_center', 'Bottom Right': 'bottom_right'
        }
        for display_text, key in anchors.items():
            self.anchor_combo.addItem(display_text, key)
        current_anchor = self.settings.get('position.anchor', 'top_left')
        self.anchor_combo.setCurrentIndex(self.anchor_combo.findData(current_anchor))
        self.anchor_combo.currentTextChanged.connect(self.update_anchor)
        layout.addRow("Anchor Point:", self.anchor_combo)

        # X Offset
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-1000, 1000)
        self.offset_x_spin.setValue(int(self.settings.get('position.offset_x', 10)))
        self.offset_x_spin.valueChanged.connect(self.update_offset_x)
        layout.addRow("Offset X (px):", self.offset_x_spin)

        # Y Offset
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-1000, 1000)
        self.offset_y_spin.setValue(int(self.settings.get('position.offset_y', 10)))
        self.offset_y_spin.valueChanged.connect(self.update_offset_y)
        layout.addRow("Offset Y (px):", self.offset_y_spin)

        # Width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3000) # Min 100px, Max 3000px
        self.width_spin.setValue(int(self.settings.get('position.width', 400)))
        self.width_spin.valueChanged.connect(self.update_width)
        layout.addRow("Width (px):", self.width_spin)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Position")

    def update_monitor(self, index):
        self.settings.set('position.monitor', index)
        self.app.watermark.update_position()

    def update_anchor(self, text):
        anchor_key = self.anchor_combo.currentData()
        self.settings.set('position.anchor', anchor_key)
        self.app.watermark.update_position()

    def update_offset_x(self, value):
        self.settings.set('position.offset_x', value)
        self.app.watermark.update_position()

    def update_offset_y(self, value):
        self.settings.set('position.offset_y', value)
        self.app.watermark.update_position()

    def update_width(self, value):
        self.settings.set('position.width', value)
        self.app.watermark.update_position()

    def create_appearance_tab(self):
        """Creates the Appearance settings tab."""
        tab = QWidget()
        layout = QFormLayout()
        
        # Font Family
        self.font_combo = QFontComboBox()
        current_font = self.settings.get('appearance.font_family', 'Arial')
        self.font_combo.setCurrentText(current_font)
        self.font_combo.currentFontChanged.connect(self.update_font_family)
        layout.addRow("Font Family:", self.font_combo)

        # Font Size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(int(self.settings.get('appearance.font_size', 12)))
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        layout.addRow("Font Size (pt):", self.font_size_spin)

        # Text Alignment
        self.align_combo = QComboBox()
        self.align_combo.addItems(['Left', 'Center', 'Right'])
        current_align = self.settings.get('appearance.text_align', 'left')
        self.align_combo.setCurrentText(current_align.capitalize())
        self.align_combo.currentTextChanged.connect(self.update_text_align)
        layout.addRow("Text Align:", self.align_combo)

        # Font Color
        self.color_button = QPushButton()
        self.current_color = QColor(self.settings.get('appearance.font_color', '#FFFFFF'))
        self.update_color_button_style()
        self.color_button.clicked.connect(self.choose_color)
        layout.addRow(QLabel("Font Color:"), self.color_button)

        # Opacity Slider
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(self.settings.get('appearance.opacity', 100)))
        opacity_label = QLabel(f"{self.opacity_slider.value()}%" )
        self.opacity_slider.valueChanged.connect(lambda value: opacity_label.setText(f"{value}%"))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(opacity_label)
        layout.addRow("Opacity:", opacity_layout)

        # Always on Top
        self.always_on_top_check = QCheckBox()
        self.always_on_top_check.setChecked(self.settings.get('window.always_on_top', True))
        self.always_on_top_check.toggled.connect(self.update_always_on_top)
        layout.addRow("Always on Top:", self.always_on_top_check)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Appearance")

    def update_font_family(self, font):
        self.settings.set('appearance.font_family', font.family())
        self.app.watermark.update_appearance()

    def update_font_size(self, size):
        self.settings.set('appearance.font_size', size)
        self.app.watermark.update_appearance()

    def update_text_align(self, align_text):
        align = align_text.lower()
        self.settings.set('appearance.text_align', align)
        self.app.watermark.update_appearance()

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.settings.set('appearance.font_color', color.name())
            self.update_color_button_style()
            self.app.watermark.update_appearance()
            
    def update_color_button_style(self):
        self.color_button.setText(self.current_color.name())
        text_color = '#000' if (self.current_color.red() * 0.299 + self.current_color.green() * 0.587 + self.current_color.blue() * 0.114) > 186 else '#FFF'
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()}; color: {text_color};")

    def update_always_on_top(self, checked):
        self.settings.set('window.always_on_top', checked)
        self.app.watermark.update_flags()

    def update_opacity(self, value):
        self.settings.set('appearance.opacity', value)
        self.app.watermark.update_appearance()

    def create_visualization_tab(self):
        """Creates the Visualization settings tab with a tree view for sensor selection."""
        tab = QWidget()
        layout = QVBoxLayout()

        self.sensor_tree = QTreeWidget()
        self.sensor_tree.setHeaderLabels(["Hardware & Sensors"])
        self.sensor_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.sensor_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.sensor_tree.itemChanged.connect(self.update_sensor_selection)
        self.sensor_tree.model().rowsMoved.connect(self.handle_rows_moved)
        layout.addWidget(self.sensor_tree)

        # Temperature Unit Selector
        unit_layout = QFormLayout()
        self.temp_unit_combo = QComboBox()
        self.temp_unit_combo.addItems(['Celsius', 'Fahrenheit'])
        current_unit = self.settings.get('monitoring.temperature_unit', 'celsius')
        self.temp_unit_combo.setCurrentText(current_unit.capitalize())
        self.temp_unit_combo.currentTextChanged.connect(self.update_temp_unit)
        unit_layout.addRow("Temperature Unit:", self.temp_unit_combo)
        layout.addLayout(unit_layout)

        populate_button = QPushButton("Refresh Hardware List")
        populate_button.clicked.connect(self.populate_sensor_tree)
        layout.addWidget(populate_button)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Visualization")

    def populate_sensor_tree(self):
        """Fills the tree with hardware and sensors."""
        self.sensor_tree.blockSignals(True)
        self.sensor_tree.clear()
        hardware_data = self.app.hardware_monitor.get_hardware_data()
        enabled_sensors = self.settings.get('visualization.enabled_sensors', {})
        is_config_empty = not any(enabled_sensors.values())

        for hw_item in hardware_data:
            hw_name = hw_item['name']
            parent = QTreeWidgetItem(self.sensor_tree, [hw_name])
            parent.setFlags(parent.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            parent.setCheckState(0, Qt.CheckState.Unchecked)

            hw_enabled_sensors = enabled_sensors.get(hw_name, [])
            all_sensors_enabled = True

            for sensor in hw_item['sensors']:
                sensor_name = sensor['name']
                child = QTreeWidgetItem(parent, [sensor_name])
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if is_config_empty or sensor_name in hw_enabled_sensors:
                    child.setCheckState(0, Qt.CheckState.Checked)
                else:
                    child.setCheckState(0, Qt.CheckState.Unchecked)
                    all_sensors_enabled = False
            
            if all_sensors_enabled and parent.childCount() > 0:
                parent.setCheckState(0, Qt.CheckState.Checked)
            elif not all_sensors_enabled and hw_enabled_sensors:
                parent.setCheckState(0, Qt.CheckState.PartiallyChecked)

        self.sensor_tree.expandAll()
        self.sensor_tree.blockSignals(False)

    def handle_rows_moved(self, parent, start, end, destination, dest_row):
        """Handles the reordering of items in the tree."""
        # Update the component order in settings
        new_order = []
        for i in range(self.sensor_tree.topLevelItemCount()):
            new_order.append(self.sensor_tree.topLevelItem(i).text(0))
        self.settings.set('visualization.component_order', new_order)

        # Update the enabled sensors order within a component if a sensor was moved
        # This logic now handles both component and sensor reordering implicitly
        # by rebuilding the enabled_sensors config based on the new tree structure.
        self.update_sensor_selection(self.sensor_tree.invisibleRootItem(), 0)

        # Force a UI update
        self.app.watermark.update_text(self.app._format_data_for_display(self.app.hardware_monitor.get_hardware_data()))

    def update_sensor_selection(self, item, column):
        """Handles changes in the sensor selection tree."""
        # Update children when a parent is checked/unchecked
        if item.childCount() > 0:
            self.sensor_tree.blockSignals(True)
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, item.checkState(0))
            self.sensor_tree.blockSignals(False)

        # Update parent state based on children
        parent = item.parent()
        if parent:
            self.sensor_tree.blockSignals(True)
            checked_count = 0
            for i in range(parent.childCount()):
                if parent.child(i).checkState(0) == Qt.CheckState.Checked:
                    checked_count += 1
            
            if checked_count == 0:
                parent.setCheckState(0, Qt.CheckState.Unchecked)
            elif checked_count == parent.childCount():
                parent.setCheckState(0, Qt.CheckState.Checked)
            else:
                parent.setCheckState(0, Qt.CheckState.PartiallyChecked)
            self.sensor_tree.blockSignals(False)

        # Save the current selection to settings
        enabled_sensors = {}
        for i in range(self.sensor_tree.topLevelItemCount()):
            hw_item = self.sensor_tree.topLevelItem(i)
            hw_name = hw_item.text(0)
            enabled_sensors[hw_name] = []
            for j in range(hw_item.childCount()):
                sensor_item = hw_item.child(j)
                if sensor_item.checkState(0) == Qt.CheckState.Checked:
                    enabled_sensors[hw_name].append(sensor_item.text(0))
        
        self.settings.set('visualization.enabled_sensors', enabled_sensors)
        # Trigger a UI update in the main app
        self.app.watermark.update_text(self.app._format_data_for_display(self.app.hardware_monitor.get_hardware_data()))

    def update_temp_unit(self, unit_text):
        """Updates the temperature unit setting."""
        unit = unit_text.lower()
        self.settings.set('monitoring.temperature_unit', unit)
        # Force a data refresh to apply the new unit
        self.app.watermark.update_text(self.app._format_data_for_display(self.app.hardware_monitor.get_hardware_data()))

    def create_about_tab(self):
        """Creates the About tab with version info and links."""
        tab = QWidget()
        layout = QVBoxLayout()

        version = self.settings.get('about.version', 'N/A')
        repo_url = self.settings.get('about.repository_url', '#')

        title_label = QLabel(f"<b>PyMonitor.NET</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; margin-bottom: 10px;")

        version_label = QLabel(f"Version: {version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description_label = QLabel("A lightweight, transparent hardware monitor built with Python and .NET.")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        repo_label = QLabel(f"<a href='{repo_url}'>Project on GitHub</a>")
        repo_label.setOpenExternalLinks(True)
        repo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lhm_version_label = QLabel("Checking LibreHardwareMonitorLib version...")
        lhm_version_label.setObjectName("lhm_version_label")
        lhm_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(description_label)
        layout.addWidget(repo_label)
        layout.addWidget(lhm_version_label)
        layout.addStretch()

        tab.setLayout(layout)
        self.tabs.addTab(tab, "About")
        self.check_lhm_version() # Trigger version check when tab is created

    def accept(self):
        """Saves settings to file and closes the dialog."""
        try:
            self.settings.save()
            print("Settings saved successfully.")
            super().accept()
        except Exception as e:
            print(f"An error occurred while saving settings: {e}", file=sys.stderr)
            # Optionally, show an error message to the user
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setText("Failed to save settings.")
            error_box.setInformativeText(str(e))
            error_box.setWindowTitle("Save Error")
            error_box.exec()

    def reject(self):
        """Restores settings to their original state and closes the dialog."""
        if self.original_settings:
            self.settings.data = copy.deepcopy(self.original_settings)
            # Re-apply all settings to the UI
            self.app.watermark.update_appearance()
            self.app.watermark.update_position()
            self.app.watermark.update_flags()
            # Force an immediate data refresh with the correct filters
            self.app.watermark.update_text(self.app._format_data_for_display(self.app.hardware_monitor.get_hardware_data()))
            # Also reset the controls in the settings window itself
            self.reset_controls_to_current_settings()

        print("Settings changes cancelled.")
        super().reject()

    def check_lhm_version(self):
        """Checks for the LHM version in a separate thread to avoid UI blocking."""
        self.lhm_version_label = self.findChild(QLabel, "lhm_version_label")

        class VersionWorker(QThread):
            finished = pyqtSignal(str, str)

            def __init__(self, app):
                super().__init__()
                self.app = app

            def run(self):
                local_version = self.app.hardware_monitor.get_local_dll_version()
                latest_version = get_latest_lhm_version()
                self.finished.emit(local_version, latest_version)

        self.version_worker = VersionWorker(self.app)
        self.version_worker.finished.connect(self.update_lhm_version_label)
        self.version_worker.start()

    def update_lhm_version_label(self, local_version, latest_version):
        """Updates the label in the About tab with version info."""
        if not self.lhm_version_label:
            return

        text = f"LibreHardwareMonitorLib Version: {local_version or 'N/A'}"
        if latest_version:
            if local_version and local_version < latest_version:
                text += f" <font color='orange'>(Update available: {latest_version})</font>"
            elif local_version == latest_version:
                text += f" <font color='green'>(Up to date)</font>"
            else:
                text += f" (Latest: {latest_version})"
        else:
            text += " (Could not check for updates)"
        
        self.lhm_version_label.setText(text)

    def reset_controls_to_current_settings(self):
        """Resets all UI controls in the dialog to reflect the current settings."""
        # Appearance Tab
        self.font_combo.setCurrentText(self.settings.get('appearance.font_family', 'Arial'))
        self.font_size_spin.setValue(int(self.settings.get('appearance.font_size', 12)))
        self.align_combo.setCurrentText(self.settings.get('appearance.text_align', 'left').capitalize())
        self.current_color = QColor(self.settings.get('appearance.font_color', '#FFFFFF'))
        self.update_color_button_style()
        self.opacity_slider.setValue(int(self.settings.get('appearance.opacity', 100)))
        self.always_on_top_check.setChecked(self.settings.get('window.always_on_top', True))

        # Visualization Tab
        self.temp_unit_combo.setCurrentText(self.settings.get('monitoring.temperature_unit', 'celsius').capitalize())

        # Position Tab
        self.monitor_combo.setCurrentIndex(self.settings.get('position.monitor', 0))
        self.anchor_combo.setCurrentIndex(self.anchor_combo.findData(self.settings.get('position.anchor', 'top_left')))
        self.offset_x_spin.setValue(int(self.settings.get('position.offset_x', 10)))
        self.offset_y_spin.setValue(int(self.settings.get('position.offset_y', 10)))
        self.width_spin.setValue(int(self.settings.get('position.width', 400)))

        # Visualization Tab
        self.populate_sensor_tree()
