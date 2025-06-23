# PyMonitor.NET

**PyMonitor.NET** is a lightweight, highly customizable hardware monitoring tool for Windows and Linux. It displays real-time system information as a transparent, click-through overlay on your desktop, allowing you to keep an eye on your system's performance without obstructing your work.

---

## Key Features

- **Real-Time Monitoring**: Tracks critical hardware stats including CPU, GPU, and RAM usage, temperatures, and more.
- **Transparent Overlay**: Displays information directly on your desktop in a clean, unobtrusive "watermark" style.
- **Click-Through Window**: The overlay is non-interactive, so you can click through it to access icons and windows underneath.
- **Highly Customizable**:
    - **Appearance**: Change font family, size, color, and opacity.
    - **Position**: Select monitor, anchor point (e.g., top-right, bottom-center), and pixel offsets.
    - **Layout**: Set a fixed width and align text (left, center, or right).
    - **Content**: Choose exactly which hardware components and sensors to display and reorder them via drag-and-drop.
- **System Tray Control**: Runs quietly in the system tray. Right-click the icon to open settings or exit the application.
- **Persistent Settings**: All your customizations are automatically saved in a `settings.json` file.
- **Single Instance**: Prevents multiple copies of the application from running simultaneously.

---

## Technology Stack

- **Frontend**: Python 3 with **PyQt6** for the graphical user interface (overlay and settings window).
- **Backend**: **.NET 8+** via the **`pythonnet`** library to interface with **LibreHardwareMonitor**.
- **Hardware Data**: Leverages the powerful `LibreHardwareMonitorLib.dll` for comprehensive hardware detection and data polling.

---

## Prerequisites

- **Python 3.10+**
- **.NET 8 SDK/Runtime** (or newer)

---

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd PyMonitor.NET
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Add LibreHardwareMonitor:**
    - Download the latest version of [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases).
    - Extract the archive.
    - Copy `LibreHardwareMonitorLib.dll` and all other related `.dll` files from the `net8.0` (or newer) directory into the root folder of this project.

---

## Usage

To run the application, execute the main module from the project's root directory:

```bash
python -m src.pymonitor.main
```

The application will start and an icon will appear in your system tray. The hardware monitor overlay will be visible on your desktop.

- **Right-click** the tray icon to open the **Settings** window or **Exit** the application.

---

## Configuration

All settings are managed through the UI and stored in the `settings.json` file in the project root. You can manually edit this file, but it's recommended to use the settings window.

- **Position**: Configure monitor, anchor, offsets, and width.
- **Appearance**: Adjust font, size, color, alignment, and opacity.
- **Visualization**: Select which hardware and sensors to display. You can also drag and drop components to change their display order.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
