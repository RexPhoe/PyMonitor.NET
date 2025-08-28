# src/pymonitor/hardware/monitor.py

import clr
import os
from System.Diagnostics import FileVersionInfo  # type: ignore # .NET library loaded at runtime


class UntrustedLocationError(Exception):
    """Exception raised when DLL is in an untrusted location that .NET blocks."""
    pass


class HardwareMonitor:
    """A wrapper for LibreHardwareMonitorLib to fetch hardware data."""

    def __init__(self, settings, lib_path=".") -> None:
        """Initializes the HardwareMonitor, preparing pythonnet to use the DLL."""
        self.settings = settings
        self.computer = None
        self.dll_path = os.path.abspath(
            os.path.join(lib_path, "LibreHardwareMonitorLib.dll")
        )

        if not os.path.exists(self.dll_path):
            raise FileNotFoundError(
                f"Could not find LibreHardwareMonitorLib.dll at {self.dll_path}"
            )

        # Check if DLL is in an untrusted location
        self._check_dll_location()

        try:
            clr.AddReference(self.dll_path)
            from LibreHardwareMonitor import Hardware  # type: ignore # .NET library loaded at runtime

            # This is a workaround for a potential pythonnet issue where the namespace
            # is not immediately available.
            self.Hardware = Hardware
        except Exception as e:
            if "0x80131515" in str(e) or "loadFromRemoteSources" in str(e):
                raise UntrustedLocationError(
                    f"Cannot load LibreHardwareMonitorLib.dll from untrusted location: {self.dll_path}\n"
                    f"This error occurs when the application is run from folders like Downloads.\n\n"
                    f"SOLUTION:\n"
                    f"1. Move the entire PyMonitor.NET folder to a trusted location like:\n"
                    f"   - C:\\Program Files\\PyMonitor.NET\n"
                    f"   - C:\\Users\\{os.getenv('USERNAME', 'YourUser')}\\Documents\\PyMonitor.NET\n"
                    f"   - C:\\PyMonitor.NET\n\n"
                    f"2. Or right-click on LibreHardwareMonitorLib.dll → Properties → Unblock\n\n"
                    f"3. Then run the application from the new location.\n\n"
                    f"Original error: {e}"
                ) from e
            else:
                raise

    def _check_dll_location(self):
        """Check if DLL is in a potentially problematic location."""
        dll_dir = os.path.dirname(self.dll_path).lower()
        problematic_paths = [
            "downloads",
            "download", 
            "temp",
            "tmp",
            "desktop\\pymonitor", # Only if it's a downloaded folder
        ]
        
        # Check if path contains problematic folders
        for problematic in problematic_paths:
            if problematic in dll_dir:
                print(f"⚠️  WARNING: Application is running from potentially untrusted location: {self.dll_path}")
                print(f"   If you encounter loading errors, move the folder to a trusted location like:")
                print(f"   - C:\\Program Files\\PyMonitor.NET")
                print(f"   - C:\\Users\\{os.getenv('USERNAME', 'YourUser')}\\Documents\\PyMonitor.NET")
                print(f"   - C:\\PyMonitor.NET")
                break

    def initialize(self) -> None:
        """Creates an instance of the Computer class from the DLL."""
        self.computer = self.Hardware.Computer()
        self.computer.IsCpuEnabled = True
        self.computer.IsGpuEnabled = True
        self.computer.IsMemoryEnabled = True
        self.computer.IsMotherboardEnabled = True
        self.computer.IsStorageEnabled = True
        self.computer.IsNetworkEnabled = True
        self.computer.Open()

    def close(self) -> None:
        """Closes the computer instance to release resources."""
        if self.computer:
            self.computer.Close()

    def get_local_dll_version(self) -> str:
        """Gets the file version of the local LibreHardwareMonitorLib.dll."""
        try:
            version_info = FileVersionInfo.GetVersionInfo(self.dll_path)
            return version_info.FileVersion
        except Exception as e:
            print(f"Could not read DLL version: {e}")
            return "N/A"

    def get_hardware_data(self) -> list:
        """Fetches and returns a structured list of hardware data."""
        if not self.computer:
            return []

        data = []
        for hardware in self.computer.Hardware:
            hardware.Update()  # Recommended to call Update() on each hardware component

            item = {
                "name": hardware.Name,
                "type": str(hardware.HardwareType),
                "sensors": [],
            }

            # --- Logic for synthetic CPU Frequency sensor ---
            is_cpu = str(hardware.HardwareType) == "Cpu"
            cpu_core_frequencies = []
            # ---

            for sensor in hardware.Sensors:
                value = sensor.Value
                formatted_value = "N/A"

                # Collect CPU core frequencies for the synthetic sensor
                if (
                    is_cpu
                    and str(sensor.SensorType) == "Clock"
                    and "Core" in sensor.Name
                    and value is not None
                ):
                    cpu_core_frequencies.append(value)

                if value is not None:
                    try:
                        unit = self._get_unit(sensor.SensorType)
                        temp_unit = self.settings.get(
                            "monitoring.temperature_unit", "celsius"
                        )

                        if (
                            "Temperature" in str(sensor.SensorType)
                            and temp_unit == "fahrenheit"
                        ):
                            value = (value * 9 / 5) + 32

                        # Special handling for data sensors (memory usage, etc.)
                        if "Data" in str(sensor.SensorType):
                            formatted_value = self._format_data_value(
                                value, sensor.Name
                            )
                        else:
                            formatted_value = f"{value:.2f} {unit}".strip()
                    except (TypeError, ValueError):
                        formatted_value = str(value)

                sensor_info = {
                    "name": sensor.Name,
                    "type": str(sensor.SensorType),
                    "value": formatted_value,
                }
                item["sensors"].append(sensor_info)

            # Add the synthetic CPU Frequency sensor if applicable
            if is_cpu and cpu_core_frequencies:
                max_freq = max(cpu_core_frequencies)
                unit = self._get_unit(self.Hardware.SensorType.Clock)
                formatted_value = f"{max_freq:.2f} {unit}".strip()

                cpu_freq_sensor = {
                    "name": "CPU Frequency",
                    "type": str(self.Hardware.SensorType.Clock),
                    "value": formatted_value,
                }
                item["sensors"].insert(0, cpu_freq_sensor)

            data.append(item)
        return data

    def _format_data_value(self, value, sensor_name):
        """Formats data values with appropriate units (bytes, MB, GB)."""
        sensor_name_lower = sensor_name.lower()

        # GPU Memory is typically in MB when it comes from LibreHardwareMonitor
        if "gpu" in sensor_name_lower and "memory" in sensor_name_lower:
            # Convert MB to GB for display if value is large
            if value >= 1024:
                return f"{value / 1024:.2f} GB"
            else:
                return f"{value:.1f} MB"

        # Network data is usually in bytes, convert appropriately
        if any(
            keyword in sensor_name_lower for keyword in ["upload", "download", "data"]
        ):
            if value >= 1024 * 1024 * 1024:  # GB
                return f"{value / (1024 * 1024 * 1024):.2f} GB"
            elif value >= 1024 * 1024:  # MB
                return f"{value / (1024 * 1024):.1f} MB"
            elif value >= 1024:  # KB
                return f"{value / 1024:.1f} KB"
            else:
                return f"{value:.0f} B"

        # Default: assume MB
        return f"{value:.1f} MB"

    def _get_unit(self, sensor_type) -> str:
        """Returns the appropriate unit for a given sensor type."""
        # This can be expanded based on the SensorType enum
        sensor_type_str = str(sensor_type)
        if "Temperature" in sensor_type_str:
            unit = self.settings.get("monitoring.temperature_unit", "celsius")
            return "°F" if unit == "fahrenheit" else "°C"
        if "Load" in sensor_type_str:
            return "%"
        if "Clock" in sensor_type_str:
            return "MHz"
        if "Power" in sensor_type_str:
            return "W"
        if "Data" in sensor_type_str:
            return "MB"  # Changed from GB to MB
        if "Fan" in sensor_type_str:
            return "RPM"
        if "Voltage" in sensor_type_str:
            return "V"
        if "Control" in sensor_type_str:
            return "%"
        return ""
