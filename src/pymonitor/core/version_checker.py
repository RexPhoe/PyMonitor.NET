# src/pymonitor/core/version_checker.py

import requests
import re

LHM_REPO_API_URL = "https://api.github.com/repos/LibreHardwareMonitor/LibreHardwareMonitor/releases/latest"

def get_latest_lhm_version(timeout=5):
    """
    Fetches the latest release version of LibreHardwareMonitor from the GitHub API.
    Returns the version string (e.g., '0.9.6') or None if an error occurs.
    """
    try:
        response = requests.get(LHM_REPO_API_URL, timeout=timeout)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        tag_name = data.get('tag_name')
        if tag_name:
            # Use regex to find a standard version pattern (e.g., 0.9.6)
            match = re.search(r'(\d+\.\d+\.\d+)', tag_name)
            if match:
                return match.group(1)
            # Fallback for tags like 'v0.9.6'
            return tag_name.lstrip('v')
        return None
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Failed to fetch latest LHM version from GitHub: {e}")
        return None
