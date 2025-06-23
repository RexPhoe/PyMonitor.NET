# PyMonitor.NET Project Structure

This document outlines the architecture and development principles for the PyMonitor.NET application. Its purpose is to ensure that future development, whether by the original author or other contributors (human or AI), adheres to a consistent and maintainable structure.

## Core Principles

1.  **Modularity and Separation of Concerns**: The project is divided into distinct modules, each with a single responsibility. For example, `hardware` handles data collection, `ui` handles presentation, and `config` handles settings. Changes in one module should not break others.
2.  **Stability over Premature Optimization**: Core components that are functioning correctly should not be modified unless necessary. For instance, once the `HardwareMonitor` class reliably fetches data, it should be considered stable.
3.  **Cross-Platform Design**: While the initial focus is on Windows, the design should accommodate future expansion to other platforms like Linux. Platform-specific code should be isolated and abstracted.
4.  **Clear Naming Conventions**: All code, including files, classes, variables, and comments, must be in English.

## Directory Structure

```
PyMonitor.NET/
├── .gitignore
├── LibreHardwareMonitorLib.dll
├── HidSharp.dll
├── requirements.txt
├── docs/
│   └── PROJECT_STRUCTURE.md
└── src/
    └── pymonitor/
        ├── __init__.py
        ├── main.py
        ├── core/
        │   ├── __init__.py
        │   └── app.py
        ├── hardware/
        │   ├── __init__.py
        │   └── monitor.py
        ├── config/
        │   ├── __init__.py
        │   └── settings.py
        └── ui/
            ├── __init__.py
            ├── settings_window.py
            ├── tray_icon.py
            └── watermark.py
```

### Module Descriptions

-   **`src/pymonitor/main.py`**: The main entry point of the application. Its sole responsibility is to initialize and run the main application object.

-   **`src/pymonitor/core/app.py`**: Contains the main `Application` class that orchestrates the different components (hardware monitoring, UI, configuration).

-   **`src/pymonitor/hardware/monitor.py`**: Handles all interaction with the `LibreHardwareMonitorLib.dll`. It is responsible for initializing the library, finding hardware components, and retrieving sensor data. This module should have no knowledge of the UI or configuration.

-   **`src/pymonitor/config/settings.py`**: Manages loading, saving, and accessing user-defined settings from a `settings.json` file. It handles all configuration, including window position, appearance (font, color, opacity), and the user-defined order of hardware components and sensors.

-   **`src/pymonitor/ui/watermark.py`**: Renders the hardware data as a desktop overlay. The window is non-interactive (click-through) and its appearance, including font, color, size, and opacity, is dynamically updated based on user settings.

-   **`src/pymonitor/ui/settings_window.py`**: Implements the main settings dialog. It features multiple tabs (Position, Appearance, Visualization, About) allowing the user to customize every aspect of the monitor. It also handles the logic for drag-and-drop reordering of hardware and sensors.

-   **`src/pymonitor/ui/tray_icon.py`**: Manages the system tray icon and its context menu, which triggers actions like opening the settings window or exiting the application.

-   **`docs/`**: Contains all project documentation.

-   **Root Directory**: Contains the .NET libraries, dependency lists, and other project-level files.

## Development Workflow

When adding a new feature or fixing a bug:

1.  **Identify the Responsible Module**: Determine which module(s) the change affects based on the descriptions above.
2.  **Isolate Changes**: Strive to limit changes to the identified module(s). If a change in one module requires a change in another, re-evaluate the design. For example, if adding a new sensor type requires changing the UI, the change should be in how the UI *interprets* data from the hardware module, not in the hardware module itself.
3.  **Preserve Stable APIs**: Do not change the public methods of a stable class (like `HardwareMonitor`) if it's working correctly. Instead, if new functionality is needed, extend the class or add new methods without altering the existing ones that other parts of the application rely on.
