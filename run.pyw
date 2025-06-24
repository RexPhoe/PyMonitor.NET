# run.pyw
import ctypes
import sys
import os

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with administrative privileges."""
    script_path = os.path.abspath(sys.argv[0])
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{script_path}"', 
            None, 
            1
        )
        if ret <= 32:
            # Handle error if ShellExecuteW fails
            # You might want to log this or show a message box
            pass
    except Exception as e:
        # Log or show error
        pass

if __name__ == "__main__":
    if is_admin():
        # Add the 'src' directory to the Python path to find the pymonitor module
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        try:
            from pymonitor.main import main
            main()
        except ImportError as e:
            # Fallback for debugging, writes to a log file since no console is visible
            with open("run_error.log", "w") as f:
                f.write(f"ImportError: {e}\n")
                f.write(f"Python Path: {sys.path}\n")
            sys.exit(1)
        except Exception as e:
            with open("run_error.log", "w") as f:
                f.write(f"An unexpected error occurred: {e}\n")
            sys.exit(1)
    else:
        # Re-run the script with admin rights and exit the current process
        run_as_admin()
        sys.exit(0)
