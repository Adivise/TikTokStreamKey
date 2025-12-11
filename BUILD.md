# Building the EXE File

## Quick Build

### Option 1: Using Batch Script (Windows)
```batch
build.bat
```

### Option 2: Using PowerShell Script (Windows)
```powershell
.\build.ps1
```

### Option 3: Manual Build
```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Build with Nuitka
python -m nuitka --assume-yes-for-downloads --standalone --onefile --windows-icon-from-ico=streamkey.ico --windows-console-mode=disable --enable-plugin=pyside6 --include-module=seleniumwire --include-module=blinker._saferef --include-package-data=seleniumwire --include-package=certifi --nofollow-import-to="*.tests" --nofollow-import-to="pydoc" --nofollow-import-to="test" --windows-company-name="Suntury" --windows-product-name="TikTok StreamKey Generator" --windows-file-description="TikTok Stream Key Generator for OBS Studio" --copyright="Copyright © 2025" --output-dir=dist main.py
```

## Build Options Explained

- `--standalone`: Creates a standalone executable with all dependencies
- `--onefile`: Creates a single EXE file (easier to distribute)
- `--windows-icon-from-ico=streamkey.ico`: Uses your icon file
- `--windows-console-mode=disable`: Hides console window (GUI app)
- `--enable-plugin=pyside6`: Enables PySide6 plugin for Qt
- `--include-module=seleniumwire`: Includes seleniumwire module
- `--include-package-data=seleniumwire`: Includes seleniumwire data files
- `--output-dir=dist`: Outputs to dist folder

## Output

After building, you'll find the EXE file in the `dist` folder:
- `dist/main.exe` (or `dist/main.dist/main.exe` if not using --onefile)

## Troubleshooting

### If build fails:
1. Make sure virtual environment is activated
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Check that `streamkey.ico` exists in the project root
4. Try building without `--onefile` first to see detailed errors

### If EXE doesn't run:
1. Check Windows Defender/antivirus isn't blocking it
2. Try running from command line to see error messages
3. Ensure all required DLLs are included (Nuitka should handle this)

### Reducing EXE size:
- Remove `--onefile` (creates a folder instead)
- Use `--enable-plugin=anti-bloat` to remove unused code
- Add `--no-pyi-file` to skip .pyi files

## Distribution

The EXE file is standalone and can be distributed without Python installed. Just copy the EXE file (or the entire dist folder if not using --onefile) to other Windows machines.

