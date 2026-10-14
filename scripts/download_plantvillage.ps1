# Downloads only PlantVillage's raw/color ImageFolder classes.
# Requires Git for Windows and a network connection.
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$target = Join-Path $repoRoot "data\plantvillage"
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("plantvillage-" + [guid]::NewGuid().ToString("N"))

if (Test-Path $target) {
    $existing = Get-ChildItem -LiteralPath $target -Force -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($existing) {
        throw "Target '$target' is not empty. Move or remove it before downloading again."
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found. Install Git for Windows, reopen PowerShell, and rerun this script."
}

try {
    Write-Host "Downloading PlantVillage raw/color using a sparse Git checkout..."
    git clone --depth 1 --filter=blob:none --sparse https://github.com/spMohanty/PlantVillage-Dataset.git $temp
    if ($LASTEXITCODE -ne 0) { throw "Git clone failed with exit code $LASTEXITCODE." }

    git -C $temp sparse-checkout set raw/color
    if ($LASTEXITCODE -ne 0) { throw "Sparse checkout failed with exit code $LASTEXITCODE." }

    $source = Join-Path $temp "raw\color"
    if (-not (Test-Path (Join-Path $source "."))) {
        throw "Expected dataset folder '$source' was not found. Check the upstream repository layout."
    }

    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force

    $classDirs = @(Get-ChildItem -LiteralPath $target -Directory)
    $imageCount = @(Get-ChildItem -LiteralPath $target -Recurse -File | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png|bmp|webp)$' }).Count
    if ($classDirs.Count -lt 2 -or $imageCount -lt 10) {
        throw "Download completed but dataset validation failed: found $($classDirs.Count) class folders and $imageCount images."
    }

    Write-Host "Dataset ready: $target"
    Write-Host "Class folders: $($classDirs.Count)"
    Write-Host "Images: $imageCount"
    Write-Host "Review the upstream dataset's license/usage terms before redistributing or using commercially."
}
finally {
    if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
