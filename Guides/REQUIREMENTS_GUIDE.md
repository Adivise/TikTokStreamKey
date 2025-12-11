# Requirements Guide

## For BUILDING the EXE

**YES, you MUST have all requirements installed** to build the EXE file.

### Required for Building:
1. **Python 3.8-3.11** (3.10 recommended)
2. **All packages from `requirements.txt`** installed in virtual environment
3. **C++ Compiler** (Visual Studio Build Tools or Clang)

### Why?
- **Nuitka** needs to be installed to compile the code
- **PySide6, seleniumbase, etc.** need to be installed so Nuitka can find and bundle them
- The build process analyzes your installed packages and includes them in the EXE

### How to Install Requirements:
```batch
# Activate virtual environment
venv\Scripts\activate

# Install all requirements
pip install -r requirements.txt
```

## For RUNNING the EXE

**NO, you DON'T need any requirements** to run the EXE file!

### Why?
- The EXE is **standalone** - it includes:
  - Python runtime
  - All Python packages (PySide6, seleniumbase, etc.)
  - All dependencies
  - Your application code

### What You Need to Run the EXE:
- **Windows 10/11** (64-bit)
- **That's it!** No Python, no pip, no packages needed

## Requirements Breakdown

### Essential for Building:
- ✅ **nuitka** - The compiler that creates the EXE
- ✅ **PySide6** - GUI framework (bundled into EXE)
- ✅ **seleniumbase** - Browser automation (bundled into EXE)
- ✅ **selenium-wire** - Network interception (bundled into EXE)
- ✅ **requests** - HTTP library (bundled into EXE)
- ✅ **blinker** - Signal library (bundled into EXE)
- ✅ **packaging** - Version comparison (bundled into EXE)

### Optional (but recommended):
- **clang** - Alternative C++ compiler (if you don't have MSVC)
- **Visual Studio Build Tools** - C++ compiler (recommended)

## Quick Check: Do I Have Everything?

Run this command to check:
```batch
venv\Scripts\activate
pip list
```

You should see all packages from `requirements.txt` listed.

## Common Issues

### "ModuleNotFoundError" during build
**Problem:** Missing requirement  
**Solution:** `pip install -r requirements.txt`

### "No module named 'nuitka'"
**Problem:** Nuitka not installed  
**Solution:** `pip install nuitka`

### EXE works on your PC but not others
**Problem:** Missing system dependencies  
**Solution:** The EXE should be standalone. If it fails, check:
- Windows version compatibility
- Antivirus blocking the EXE
- Missing Visual C++ Redistributables (usually auto-included)

## Summary

| Scenario | Need Requirements? |
|----------|-------------------|
| Building EXE | ✅ YES - Install all from requirements.txt |
| Running EXE | ❌ NO - EXE is standalone |
| Developing/Running Python script | ✅ YES - Install all from requirements.txt |

