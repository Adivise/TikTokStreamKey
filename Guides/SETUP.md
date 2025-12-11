# Setup Guide

## Installation

A virtual environment has been created to avoid permission issues on Windows.

### To activate the virtual environment:

**PowerShell:**
```powershell
.\venv\Scripts\activate
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

### To install/update packages:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### To run the application:

```powershell
.\venv\Scripts\python.exe StreamLabsTikTokStreamKeyGenerator.py
```

Or after activating the venv:
```powershell
python StreamLabsTikTokStreamKeyGenerator.py
```

## Alternative Solutions (if you still get permission errors)

### Option 1: Use --user flag (installs to user directory)
```powershell
pip install --user -r requirements.txt
```

### Option 2: Run PowerShell as Administrator
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Navigate to project directory
4. Run installation commands

### Option 3: Use Python's built-in pip module
```powershell
python -m pip install -r requirements.txt
```

## Troubleshooting

If you encounter permission errors:
1. Close any Python processes that might be using pip
2. Make sure no antivirus is blocking the installation
3. Try running the command prompt/PowerShell as Administrator
4. Use the virtual environment (recommended)

