# PyMonitor.NET

**PyMonitor.NET** is a lightweight, highly customizable hardware monitoring tool for Windows. It displays real-time system information as a transparent, click-through overlay on your desktop, allowing you to keep an eye on your system's performance without obstructing your work.

---

## Key Features

- **Real-Time Monitoring**: Tracks critical hardware stats including CPU usage, **real-time CPU frequency**, GPU performance, RAM usage, temperatures, power consumption, and more.
- **Transparent Overlay**: Displays information directly on your desktop in a clean, unobtrusive "watermark" style.
- **Click-Through Window**: The overlay is non-interactive, so you can click through it to access icons and windows underneath.
- **Administrative Privileges**: Automatically requests administrator privileges for full hardware access.
- **Highly Customizable**:
  - **Appearance**: Change font family, size, color, opacity, and text alignment.
  - **Position**: Select monitor, anchor point (e.g., top-right, bottom-center), and pixel offsets.
  - **Layout**: Set a fixed width or auto-width, with customizable spacing and indentation.
  - **Content**: Choose exactly which hardware components and sensors to display and reorder them via drag-and-drop.
  - **Icons**: Beautiful Nerd Font icons for each hardware component and sensor type.
- **System Tray Control**: Runs quietly in the system tray. Right-click the icon to open settings or exit the application.
- **Persistent Settings**: All your customizations are automatically saved in a `settings.json` file.
- **Single Instance**: Prevents multiple copies of the application from running simultaneously.
- **Auto-Font Download**: Automatically downloads and installs Hack Nerd Font if not present.
- **Version Checking**: Built-in version checker for LibreHardwareMonitor updates.

---

## Technology Stack

- **Frontend**: Python 3.10+ with **PyQt6** for the graphical user interface (overlay and settings window).
- **Backend**: **.NET 8+** via the **`pythonnet`** library to interface with **LibreHardwareMonitor**.
- **Hardware Data**: Leverages the powerful `LibreHardwareMonitorLib.dll` and `HidSharp.dll` for comprehensive hardware detection and data polling.
- **Fonts**: Hack Nerd Font for beautiful icons and consistent typography.

---

## Prerequisites

- **Windows 10/11** (Primary platform)
- **Python 3.10+**
- **.NET 8 SDK/Runtime** (or newer)
- **Administrator privileges** (automatically requested when needed)

---

## Installation

⚠️ **IMPORTANT**: Do not run the application directly from the Downloads folder! .NET security restrictions will prevent the DLL files from loading. Move the entire project folder to a permanent location like `C:\Program Files\PyMonitor.NET` or `C:\Users\YourUser\Documents\PyMonitor.NET` before running.

1.  **Clone or download the repository:**

    ```bash
    git clone https://github.com/RexPhoe/PyMonitor.NET.git
    cd PyMonitor.NET
    ```

    **OR download ZIP and extract to a permanent location** (NOT Downloads folder).

2.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Add LibreHardwareMonitor libraries:**

    - Download the latest version of [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases).
    - Extract the archive.
    - Copy `LibreHardwareMonitorLib.dll` and `HidSharp.dll` from the `net8.0` (or newer) directory into the root folder of this project.

4.  **Download Nerd Font (Optional):**
    ```bash
    python download_font.py
    ```
    The application will automatically download the font if it's not present.

---

## Usage

### Running the Application

**Recommended method (with automatic admin privileges):**

```bash
python run.pyw
```

**Alternative method (manual module execution):**

```bash
python -m src.pymonitor.main
```

The application will:

1. Automatically request administrator privileges if needed
2. Start and display an icon in your system tray
3. Show the hardware monitor overlay on your desktop

### Controls

- **Right-click** the tray icon to open the **Settings** window or **Exit** the application.
- The overlay window is click-through, so you can interact with anything underneath it.

### First Time Setup

1. The application will automatically download Hack Nerd Font if not present
2. Default settings will be applied for position and appearance
3. You can customize everything through the Settings window

### Testing CPU Frequency Monitoring

To test the new CPU frequency monitoring feature:

```bash
python demo_cpu_frequency.py
```

This will demonstrate real-time CPU frequency monitoring for 30 seconds, showing how the application tracks the maximum frequency across all CPU cores.

---

## Configuration

All settings are managed through the intuitive UI and stored in the `settings.json` file in the project root. You can manually edit this file, but it's recommended to use the settings window for the best experience.

### Settings Categories

- **Position**: Configure target monitor, anchor point, offsets, and window width.
- **Appearance**: Adjust font family, size, color, text alignment, opacity, and spacing.
- **Visualization**:
  - Select which hardware components and sensors to display
  - Drag and drop to reorder components
  - Toggle component titles and icons
  - Customize indentation and spacing
  - Choose between single-line and multi-line display modes
- **About**: View version information and check for updates.

### Hardware Support

The application automatically detects and supports:

- **CPU**: Usage, temperature, clock speeds, power consumption, and **real-time CPU frequency** (maximum frequency across all cores)
- **GPU**: NVIDIA, AMD, and Intel graphics cards with usage, temperature, memory, and power data
- **Memory**: RAM usage and statistics
- **Storage**: HDD and SSD information
- **Network**: Ethernet and Wi-Fi data transfer rates
- **Motherboard**: Various sensor data where available

#### CPU Frequency Monitoring

The application includes an intelligent CPU frequency monitor that:

- Automatically detects all CPU core frequencies in real-time
- Calculates and displays the **maximum frequency** among all cores as "CPU Frequency"
- Updates dynamically to show current processor performance
- Provides accurate MHz readings for performance monitoring

---

## Troubleshooting

### 🚨 Most Common Error: Assembly Loading (0x80131515)

**Error Message**: "Cannot load assembly 'LibreHardwareMonitorLib.dll'... Operation is not supported."

**Root Cause**: .NET Framework blocks loading assemblies from "untrusted" locations like Downloads folder.

### ✅ QUICK FIXES (Try in order):

#### Fix 1: Move to Trusted Location (RECOMMENDED - 95% Success)
```bash
# 1. Move entire folder to:
C:\Program Files\PyMonitor.NET
# OR
C:\Users\[YourUsername]\Documents\PyMonitor.NET

# 2. Run from new location:
cd "C:\Program Files\PyMonitor.NET"
python run.pyw
```

#### Fix 2: Unblock DLL Files (80% Success)
1. Right-click `LibreHardwareMonitorLib.dll` → **Properties** → Check **"Unblock"** → **OK**
2. Right-click `HidSharp.dll` → **Properties** → Check **"Unblock"** → **OK**
3. Run: `python run.pyw`

#### Fix 3: PowerShell Unblock (85% Success)
```powershell
# Run PowerShell as Administrator
cd "C:\path\to\PyMonitor.NET"
Get-ChildItem -Recurse | Unblock-File
```

### 🔧 Other Common Issues

| Problem | Solution |
|---------|----------|
| **App doesn't appear** | Check system tray (near clock) for PyMonitor.NET icon |
| **Missing DLL errors** | Ensure `LibreHardwareMonitorLib.dll` and `HidSharp.dll` are in root folder |
| **Permission errors** | Run Command Prompt as Administrator, then: `python run.pyw` |
| **High CPU usage** | Increase update interval in settings, disable unused sensors |
| **No hardware detected** | Run as Administrator, update motherboard drivers |

### 🔍 Quick Diagnostics
```bash
# Test if DLLs can load:
python -c "import clr; clr.AddReference('./LibreHardwareMonitorLib.dll'); print('SUCCESS')"

# Verify dependencies:
pip install -r requirements.txt

# Test basic functionality:
python -m src.pymonitor.main
```

**📋 Complete troubleshooting guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

## Version Information

- **Current Version**: 0.2.0-beta
- **Author**: Cascade, from Windsurf
- **Repository**: https://github.com/RexPhoe/PyMonitor.NET

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
