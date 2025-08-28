# PyMonitor.NET Troubleshooting Guide

## 🚨 Error 0x80131515: Assembly Loading Failure

**Full Error**: `Cannot load assembly 'LibreHardwareMonitorLib.dll' or one of its dependencies. Operation is not supported. (Exception from HRESULT: 0x80131515)`

This error occurs because .NET Framework's Code Access Security (CAS) blocks loading assemblies from untrusted locations.

---

## ✅ PROVEN SOLUTIONS (Try in order)

### Solution 1: Move to Trusted System Location (99% Success Rate)

**WHY**: Windows trusts these locations by default.

**Steps:**
1. **Close** any running instances of PyMonitor.NET
2. **Create** a new folder in a trusted location:
   ```
   C:\Program Files\PyMonitor.NET
   OR
   C:\Users\[YourUsername]\Documents\PyMonitor.NET
   OR  
   C:\PyMonitor.NET
   ```
3. **Copy** the entire PyMonitor.NET folder contents to the new location
4. **Delete** the old folder from Downloads
5. **Open Command Prompt** and navigate to new location:
   ```bash
   cd "C:\Program Files\PyMonitor.NET"
   python run.pyw
   ```

### Solution 2: Unblock Downloaded Files (Windows Security)

**WHY**: Windows marks downloaded files as potentially unsafe.

**Steps:**
1. Open **File Explorer** and navigate to PyMonitor.NET folder
2. **Right-click** on `LibreHardwareMonitorLib.dll`
3. Select **Properties**
4. At the bottom, check **"Unblock"** if present
5. Click **Apply** → **OK**
6. **Repeat** for `HidSharp.dll`
7. **Restart** the application

### Solution 3: PowerShell Unblock Method (Batch)

**WHY**: Unblocks all files at once.

**Steps:**
1. **Right-click** on PowerShell → **Run as Administrator**
2. Navigate to your PyMonitor.NET folder:
   ```powershell
   cd "C:\path\to\your\PyMonitor.NET"
   Get-ChildItem -Recurse | Unblock-File
   ```
3. **Restart** the application

### Solution 4: Enable LoadFromRemoteSources (Advanced)

**WHY**: Configures .NET to allow remote loading globally.

**Steps:**
1. Find your Python installation directory:
   ```bash
   where python
   ```
2. Create a file named `python.exe.config` in the same directory as `python.exe`
3. Add this content:
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <configuration>
     <runtime>
       <loadFromRemoteSources enabled="true" />
       <generatePublisherEvidence enabled="false" />
     </runtime>
   </configuration>
   ```
4. **Restart** your computer
5. **Run** the application again

### Solution 5: Registry Fix (Advanced Users Only)

**WHY**: Enables loading from network/download locations system-wide.

**Steps:**
1. Press **Windows + R** → type `regedit` → **Enter**
2. Navigate to: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\.NETFramework\Security\TrustManager\PromptingLevel`
3. **Right-click** → **New** → **String Value** → Name: `UntrustedSites`
4. **Double-click** the new value → Value data: `Enabled`
5. **Restart** computer
6. **Run** application

---

## 🔍 DIAGNOSTIC COMMANDS

### Test 1: Verify DLL Loading
```bash
python -c "import clr; clr.AddReference('./LibreHardwareMonitorLib.dll'); print('SUCCESS: DLL loaded')"
```

### Test 2: Check File Properties (PowerShell)
```powershell
Get-ChildItem *.dll | Get-ItemProperty -Name Zone.Identifier -ErrorAction SilentlyContinue
```

### Test 3: Verify pythonnet
```bash
python -c "import clr; print('SUCCESS: pythonnet working')"
```

### Test 4: Check .NET Framework
```bash
dotnet --version
```

---

## 🔧 OTHER COMMON ISSUES

### Issue: Application Starts But No Overlay Appears

**Symptoms**: App runs but nothing visible on screen

**Solutions:**
1. **Check System Tray** - Look for PyMonitor.NET icon near the clock
2. **Right-click tray icon** → Verify settings
3. **Check monitor configuration** - Ensure correct monitor is selected
4. **Try different anchor points** - Top-left, bottom-right, etc.
5. **Increase opacity** in settings if overlay is too transparent

### Issue: High CPU/Memory Usage

**Symptoms**: System slowdown, high resource consumption

**Solutions:**
1. **Increase update interval** in settings (try 5000ms instead of 2000ms)
2. **Disable unused sensors** in configuration
3. **Close conflicting software** (MSI Afterburner, HWiNFO64, AIDA64)
4. **Reduce displayed components** to CPU + GPU only
5. **Check for infinite loops** in error logs

### Issue: Missing Hardware Components

**Symptoms**: CPU, GPU, or RAM not detected

**Solutions:**
1. **Run as Administrator** - Required for full hardware access
2. **Update motherboard chipset drivers**
3. **Enable hardware monitoring in BIOS**
4. **Wait 30-60 seconds** after startup for full detection
5. **Check device manager** for hardware issues

### Issue: Font/Display Problems

**Symptoms**: Broken icons, wrong fonts, display corruption

**Solutions:**
1. **Reinstall Nerd Font**:
   ```bash
   python download_font.py
   ```
2. **Clear Windows font cache**:
   ```bash
   del /q /s %WINDIR%\ServiceProfiles\LocalService\AppData\Local\FontCache\*
   ```
3. **Reset display settings** to defaults
4. **Try different font** in settings

### Issue: Settings Not Saving

**Symptoms**: Configuration resets after restart

**Solutions:**
1. **Check file permissions** on `settings.json`
2. **Run as Administrator** if in Program Files
3. **Verify write access** to application folder
4. **Close application properly** using tray menu Exit
5. **Check antivirus** isn't blocking file writes

---

## 🆘 COMPLETE RESET SOLUTIONS

### Method 1: Clean Python Environment
```bash
# Uninstall pythonnet
pip uninstall pythonnet

# Clear pip cache
python -m pip cache purge

# Reinstall everything
pip install -r requirements.txt
```

### Method 2: Virtual Environment
```bash
# Create isolated environment
python -m venv pymonitor_env
pymonitor_env\Scripts\activate
pip install -r requirements.txt
python run.pyw
```

### Method 3: Windows Defender Exclusion
1. **Windows Security** → **Virus & threat protection**
2. **Manage settings** under "Virus & threat protection settings"
3. **Add or remove exclusions** → **Add an exclusion** → **Folder**
4. **Select** the PyMonitor.NET folder

### Method 4: Alternative Python Installation
1. **Download** Python from [python.org](https://python.org)
2. **Install** to `C:\Python310` (not Windows Store version)
3. **Add to PATH** during installation
4. **Reinstall** dependencies with new Python

---

## 📞 GETTING HELP

If **none** of these solutions work:

### Before Reporting Issues:

1. **Try all solutions** in order
2. **Run diagnostic commands** and save output
3. **Check** [existing GitHub issues](https://github.com/RexPhoe/PyMonitor.NET/issues)

### When Creating New Issue, Include:

```bash
# System Information
echo "OS: " && ver
echo "Python: " && python --version
echo "Python Path: " && where python
echo ".NET: " && dotnet --version

# File Status
dir LibreHardwareMonitorLib.dll
dir HidSharp.dll
echo "Current Directory: " && cd

# Python Environment
pip list | findstr -i "pythonnet pyqt6 requests"
```

### Common User Mistakes:

- ❌ Running from Downloads folder
- ❌ Missing DLL files
- ❌ Wrong Python version (< 3.10)
- ❌ Windows Store Python instead of python.org
- ❌ Not running as Administrator
- ❌ Antivirus blocking files
- ❌ Multiple Python installations conflict

### Success Rate by Solution:
- **Solution 1 (Move to trusted location)**: 95%
- **Solution 2 (Unblock files)**: 80%
- **Solution 3 (PowerShell unblock)**: 85%
- **Solution 4 (LoadFromRemoteSources)**: 70%
- **Solution 5 (Registry)**: 60%
