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

# Build with Nuitka (optimized for speed and size)
python -m nuitka --assume-yes-for-downloads --standalone --onefile --jobs=4 --windows-icon-from-ico=streamkey.ico --windows-console-mode=disable --enable-plugin=pyside6 --enable-plugin=anti-bloat --include-module=seleniumwire --include-module=blinker._saferef --include-package-data=seleniumwire --include-package=certifi --nofollow-import-to="*.tests" --nofollow-import-to="pydoc" --nofollow-import-to="test" --no-pyi-file --remove-output --windows-company-name="Suntury" --windows-product-name="TikTok StreamKey Generator" --windows-file-description="TikTok Stream Key Generator for OBS Studio" --copyright="Copyright © 2025" --output-dir=dist main.py
```

## Build Options Explained

- `--standalone`: Creates a standalone executable with all dependencies
- `--onefile`: Creates a single EXE file (easier to distribute)
- `--jobs=4`: Uses 4 parallel jobs for faster compilation (adjust based on CPU cores)
- `--windows-icon-from-ico=streamkey.ico`: Uses your icon file
- `--windows-console-mode=disable`: Hides console window (GUI app)
- `--enable-plugin=pyside6`: Enables PySide6 plugin for Qt
- `--enable-plugin=anti-bloat`: Removes unused code to reduce file size
- `--include-module=seleniumwire`: Includes seleniumwire module
- `--include-package-data=seleniumwire`: Includes seleniumwire data files
- `--no-pyi-file`: Skips .pyi type stub files (reduces size)
- `--remove-output`: Removes build cache after completion (saves disk space)
- `--output-dir=dist`: Outputs to dist folder

## Performance Optimizations

The build scripts are optimized for faster builds and smaller executables:
- **Parallel compilation** (`--jobs=4`) speeds up builds by using multiple CPU cores
- **Anti-bloat plugin** removes unused code, reducing executable size
- **No .pyi files** skips type stubs that aren't needed at runtime
- **Remove output** cleans up build cache automatically

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
- Already optimized! The build scripts include `--enable-plugin=anti-bloat` and `--no-pyi-file`
- Remove `--onefile` (creates a folder instead) - but this makes distribution harder
- Use `--lto=yes` for link-time optimization (slower build, smaller output)

### Speeding up builds:
- Already optimized! The build scripts include `--jobs=4` for parallel compilation
- Increase `--jobs` value if you have more CPU cores (e.g., `--jobs=8` for 8-core CPU)
- Use `ccache` on Linux for faster recompilation (already configured in GitHub Actions)

## Distribution

The EXE file is standalone and can be distributed without Python installed. Just copy the EXE file (or the entire dist folder if not using --onefile) to other Windows machines.

