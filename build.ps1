# PowerShell build script for TikTok StreamKey Generator
Write-Host "Building TikTok StreamKey Generator EXE..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Build with Nuitka (optimized for speed and size)
python -m nuitka `
    --assume-yes-for-downloads `
    --standalone `
    --onefile `
    --clang `
    --jobs=4 `
    --windows-icon-from-ico=streamkey.ico `
    --windows-console-mode=disable `
    --enable-plugin=pyside6 `
    --enable-plugin=anti-bloat `
    --include-module=seleniumwire `
    --include-module=blinker._saferef `
    --include-package-data=seleniumwire `
    --include-package=certifi `
    --nofollow-import-to="*.tests" `
    --nofollow-import-to="pydoc" `
    --nofollow-import-to="test" `
    --no-pyi-file `
    --remove-output `
    --windows-company-name="Suntury" `
    --windows-product-name="TikTok StreamKey | Generator" `
    --windows-file-description="TikTok Stream Key Generator for OBS Studio" `
    --windows-file-version=3.0.0 `
    --windows-product-version=3.0.0 `
    --copyright="Copyright © 2025" `
    --output-dir=dist `
    main.py

Write-Host ""
Write-Host "Build complete! Check the dist folder for the EXE file." -ForegroundColor Green

