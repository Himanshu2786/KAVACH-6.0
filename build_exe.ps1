# ============================================================================
# KAVACH 6.0 Desktop — PowerShell Build Script
# Packages standalone desktop executable in dist/KAVACH/
# ============================================================================

Write-Host "[KAVACH] Starting PyInstaller Build..." -ForegroundColor Cyan
python -m PyInstaller --clean --noconfirm KAVACH.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] KAVACH.exe successfully compiled!" -ForegroundColor Green
    Write-Host "Distribution folder: dist\KAVACH\" -ForegroundColor Green
    Write-Host "You can now copy the complete dist\KAVACH\ folder to any Windows machine." -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
