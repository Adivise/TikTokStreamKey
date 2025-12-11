# Build Troubleshooting Guide

## Common Build Errors and Solutions

### Error: "No tool module 'ilink' found"

This error occurs when Nuitka can't find a proper C++ compiler. Here are solutions:

#### Solution 1: Install Visual Studio Build Tools (Recommended)

1. Download **Visual Studio Build Tools** from: https://visualstudio.microsoft.com/downloads/
2. During installation, select:
   - **Desktop development with C++**
   - **Windows 10/11 SDK**
3. Restart your computer
4. Run the build script again

#### Solution 2: Use MSVC Compiler

If you have Visual Studio installed, use the MSVC build script:
```batch
build-msvc.bat
```

#### Solution 3: Install Clang

1. Download Clang from: https://github.com/llvm/llvm-project/releases
2. Or install via Chocolatey: `choco install llvm`
3. Add Clang to your PATH
4. Run the build script again

#### Solution 4: Use MinGW (Alternative)

If you have MinGW installed:
```batch
python -m nuitka --mingw64 --standalone --onefile ... main.py
```

### Error: "Failed unexpectedly in Scons C backend compilation"

This usually means:
- Missing C++ compiler
- Corrupted Nuitka installation
- Missing Windows SDK

**Solutions:**
1. Reinstall Nuitka: `pip install --upgrade --force-reinstall nuitka`
2. Install Visual Studio Build Tools (see Solution 1 above)
3. Clear Nuitka cache: Delete `main.build` and `main.dist` folders if they exist

### Error: "Chrome not found" or Selenium issues

This is a runtime error, not a build error. The EXE will still build, but the "Load from Web" feature won't work without Chrome installed on the target machine.

### Build Takes Too Long

The first build can take 10-30 minutes. To speed up:
- Remove `--onefile` (creates a folder instead, but builds faster)
- Use `--jobs=4` to use multiple CPU cores
- Close other applications

### EXE File Size is Too Large

To reduce size:
- Remove `--onefile` (but then you need to distribute the entire folder)
- Add `--enable-plugin=anti-bloat` to remove unused code
- Use `--no-pyi-file` to skip type stub files

## Quick Fixes

### If build keeps failing:

1. **Clean previous builds:**
   ```batch
   rmdir /s /q main.build main.dist dist
   ```

2. **Update Nuitka:**
   ```batch
   pip install --upgrade nuitka
   ```

3. **Try without onefile first:**
   Remove `--onefile` from build script to see detailed errors

4. **Check Python version:**
   Make sure you're using Python 3.8-3.11 (3.10 recommended)

## System Requirements for Building

- **Windows 10/11**
- **Python 3.8-3.11**
- **C++ Compiler:**
  - Visual Studio Build Tools 2019 or later (recommended)
  - OR Clang 10.0 or later
  - OR MinGW-w64
- **At least 4GB RAM**
- **5-10GB free disk space** (for build cache)

## Getting Help

If you continue to have issues:
1. Check Nuitka documentation: https://nuitka.net/doc/user-manual.html
2. Check the `nuitka-crash-report.xml` file for detailed error information
3. Try building a simple test script first to verify your setup

