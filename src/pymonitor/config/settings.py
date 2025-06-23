# src/pymonitor/config/settings.py

import json
import os
import sys
import collections.abc

class Settings:
    """Manages the application's user-configurable settings."""

    def __init__(self, settings_path='settings.json'):
        self.path = settings_path
        self.data = self._load_defaults()
        self.load()

    def _load_defaults(self):
        """Returns a dictionary with the default settings."""
        return {

            'appearance': {
                'font_family': 'Arial',
                'font_size': 12,
                'font_color': '#FFFFFF',
                'opacity': 100,
                'text_align': 'left' # left, center, right
            },
            'position': {
                'monitor': 0, # Index of the monitor
                'anchor': 'top_left', # e.g., 'top_left', 'center', 'bottom_right'
                'offset_x': 10,
                'offset_y': 10,
                'width': 400 # Width of the watermark window in pixels
            },
            'visualization': {
                'enabled_sensors': {},
                'component_order': [],
                'show_component_titles': True,
                'sensor_indentation': 4,
                'category_spacing': 1,  # Number of blank lines
                'display_mode': 'multiline'  # 'multiline' or 'singleline'
            },
            'monitoring': {
                'update_interval': 2, # in seconds
                'temperature_unit': 'celsius', # celsius or fahrenheit
                'enabled_hardware': ['Cpu', 'GpuNvidia', 'Memory'], # Default hardware types
                'enabled_sensors': {
                    # Example: 'Cpu': ['CPU Total', 'CPU Package']
                },
                'order': {
                    'hardware': ['Cpu', 'GpuNvidia', 'Memory'],
                    'sensors': {}
                }
            },
            'about': {
                'version': '0.2.0-beta',
                'author': 'Cascade, from Windsurf',
                'repository_url': 'https://github.com/RexPhoe/PyMonitor.NET'
            }
        }

    def get(self, key, default=None):
        """Gets a setting value using dot notation (e.g., 'window.anchor')."""
        keys = key.split('.')
        value = self.data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key, value):
        """Sets a setting value using dot notation."""
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def save(self):
        """Saves the current settings to the file."""
        print(f"Saving settings to: {self.path}")
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=4)
            print("Settings saved successfully.")
        except IOError as e:
            print(f"Error saving settings to file: {e}", file=sys.stderr)
            raise

    def load(self):
        """Loads settings from the file, merging with defaults."""
        if not os.path.exists(self.path):
            print("Settings file not found. Creating with default values.")
            self.save()
            return

        try:
            with open(self.path, 'r') as f:
                user_settings = json.load(f)
            
            # Deep merge user settings into defaults
            self.data = self._deep_update(self._load_defaults(), user_settings)
            print("Settings loaded successfully.")

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}. Using default settings.", file=sys.stderr)
            self.data = self._load_defaults()

    def _deep_update(self, d, u):
        """Recursively update a dictionary."""
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self._deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
