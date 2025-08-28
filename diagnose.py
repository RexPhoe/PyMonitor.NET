#!/usr/bin/env python3
"""
PyMonitor.NET Diagnostic Tool
Automatically detects and helps fix common issues.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_warning(message):
    """Print warning message."""
    print(f"⚠️  {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.10+")
        print_info("Download from: https://python.org")
        return False

def check_windows_version():
    """Check Windows version."""
    if platform.system() == "Windows":
        version = platform.version()
        print_success(f"Windows {platform.release()} ({version})")
        return True
    else:
        print_error(f"Unsupported OS: {platform.system()}")
        return False

def check_dll_files():
    """Check if required DLL files exist."""
    dll_files = ["LibreHardwareMonitorLib.dll", "HidSharp.dll"]
    all_found = True
    
    for dll in dll_files:
        if os.path.exists(dll):
            print_success(f"Found: {dll}")
        else:
            print_error(f"Missing: {dll}")
            all_found = False
    
    if not all_found:
        print_info("Download from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases")
        print_info("Copy from the 'net8.0' folder to PyMonitor.NET root directory")
    
    return all_found

def check_dll_blocked():
    """Check if DLL files are blocked by Windows."""
    dll_files = ["LibreHardwareMonitorLib.dll", "HidSharp.dll"]
    blocked_files = []
    
    for dll in dll_files:
        if os.path.exists(dll):
            # Check for Zone.Identifier (Windows file blocking)
            zone_file = dll + ":Zone.Identifier"
            try:
                # Try to detect if file is blocked
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-ItemProperty -Path '{dll}' -Name Zone.Identifier -ErrorAction SilentlyContinue"],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout.strip():
                    blocked_files.append(dll)
                    print_warning(f"Blocked: {dll}")
                else:
                    print_success(f"Unblocked: {dll}")
            except:
                print_info(f"Cannot check block status: {dll}")
    
    if blocked_files:
        print_error("Some DLL files are blocked by Windows security!")
        print_info("SOLUTION: Right-click each DLL → Properties → Check 'Unblock' → OK")
        print_info("OR run: Get-ChildItem *.dll | Unblock-File  (in PowerShell as Admin)")
        return False
    
    return True

def check_location():
    """Check if running from a trusted location."""
    current_path = os.path.abspath(".").lower()
    problematic_paths = ["downloads", "download", "temp", "tmp", "desktop"]
    
    for problematic in problematic_paths:
        if problematic in current_path:
            print_error(f"Running from untrusted location: {os.path.abspath('.')}")
            print_info("SOLUTION: Move entire folder to trusted location:")
            print_info("  • C:\\Program Files\\PyMonitor.NET")
            print_info("  • C:\\Users\\[Username]\\Documents\\PyMonitor.NET")
            print_info("  • C:\\PyMonitor.NET")
            return False
    
    print_success(f"Running from trusted location: {os.path.abspath('.')}")
    return True

def check_dependencies():
    """Check if Python dependencies are installed."""
    required_packages = {
        'pythonnet': 'pythonnet',
        'PyQt6': 'PyQt6.QtCore',
        'requests': 'requests'
    }
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_success(f"Installed: {package_name}")
        except ImportError:
            print_error(f"Missing: {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print_info("SOLUTION: pip install -r requirements.txt")
        return False
    
    return True

def test_dll_loading():
    """Test if .NET DLLs can be loaded."""
    try:
        import clr
        clr.AddReference("./LibreHardwareMonitorLib.dll")
        print_success("DLL loading test passed")
        return True
    except Exception as e:
        print_error(f"DLL loading failed: {e}")
        if "0x80131515" in str(e):
            print_error("This is the untrusted location error!")
            print_info("SOLUTION: Move to trusted location or unblock DLL files")
        return False

def check_admin_privileges():
    """Check if running with admin privileges."""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        # Windows
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
    
    if is_admin:
        print_success("Running with Administrator privileges")
    else:
        print_warning("Not running as Administrator")
        print_info("Some hardware sensors may not be accessible")
        print_info("SOLUTION: Run Command Prompt as Administrator")
    
    return is_admin

def check_dotnet():
    """Check .NET installation."""
    try:
        result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f".NET Core/5+ installed: {version}")
            return True
        else:
            print_warning(".NET Core/5+ not found")
    except:
        print_warning(".NET Core/5+ not found")
    
    # Check .NET Framework via registry (Windows only)
    try:
        result = subprocess.run(
            ["reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP", "/s"],
            capture_output=True, text=True, timeout=10
        )
        if ".NET Framework" in result.stdout:
            print_info(".NET Framework detected")
            return True
    except:
        pass
    
    print_error("No compatible .NET installation found")
    print_info("SOLUTION: Install .NET 8 Runtime from: https://dotnet.microsoft.com/download")
    return False

def provide_solutions():
    """Provide comprehensive solutions based on detected issues."""
    print_header("RECOMMENDED SOLUTIONS")
    
    print("\n🎯 STEP-BY-STEP SOLUTION:")
    print("1. MOVE TO TRUSTED LOCATION (Most Important)")
    print("   • Copy entire PyMonitor.NET folder to: C:\\Program Files\\PyMonitor.NET")
    print("   • Delete old folder from Downloads")
    print("   • Run from new location")
    
    print("\n2. UNBLOCK DLL FILES")
    print("   • Right-click LibreHardwareMonitorLib.dll → Properties → Unblock")
    print("   • Right-click HidSharp.dll → Properties → Unblock")
    
    print("\n3. INSTALL DEPENDENCIES")
    print("   • pip install -r requirements.txt")
    
    print("\n4. RUN AS ADMINISTRATOR")
    print("   • Open Command Prompt as Administrator")
    print("   • cd \"C:\\Program Files\\PyMonitor.NET\"")
    print("   • python run.pyw")
    
    print("\n5. IF STILL FAILING:")
    print("   • Check antivirus isn't blocking files")
    print("   • Try different Python installation (not Windows Store version)")
    print("   • Create virtual environment: python -m venv venv")

def main():
    """Main diagnostic function."""
    print_header("PyMonitor.NET Diagnostic Tool")
    print("This tool will help identify and fix common issues.\n")
    
    all_checks_passed = True
    
    # System checks
    print_header("SYSTEM REQUIREMENTS")
    all_checks_passed &= check_windows_version()
    all_checks_passed &= check_python_version()
    all_checks_passed &= check_dotnet()
    
    # File checks
    print_header("FILE VERIFICATION")
    all_checks_passed &= check_dll_files()
    all_checks_passed &= check_dll_blocked()
    
    # Location and security checks
    print_header("SECURITY & LOCATION")
    all_checks_passed &= check_location()
    check_admin_privileges()  # Warning only, not required
    
    # Dependency checks
    print_header("PYTHON DEPENDENCIES")
    all_checks_passed &= check_dependencies()
    
    # Functional tests
    print_header("FUNCTIONALITY TESTS")
    if all_checks_passed:
        test_dll_loading()
    
    # Provide solutions
    if not all_checks_passed:
        provide_solutions()
    else:
        print_header("ALL CHECKS PASSED")
        print_success("PyMonitor.NET should work correctly!")
        print_info("If you still have issues, run: python run.pyw")
    
    print(f"\n{'='*60}")
    print("For more help, see: TROUBLESHOOTING.md")
    print("Report issues at: https://github.com/RexPhoe/PyMonitor.NET/issues")
    print('='*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Diagnostic tool error: {e}")
        print("Please report this issue on GitHub")
