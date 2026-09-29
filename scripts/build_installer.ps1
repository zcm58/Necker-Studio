param(
    [switch]$BundleOnly,
    [string]$ExistingBundle = '',
    [string]$Iscc = ''
)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$python = Join-Path $project '.venv\Scripts\python.exe'
if (-not $ExistingBundle) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $bundle = Join-Path $project "build\$stamp\bundle"
    & $python (Join-Path $PSScriptRoot 'build_bundle.py') --output $bundle
    if ($LASTEXITCODE -ne 0) { throw 'Bundle build or validation failed.' }
} else {
    $bundle = (Resolve-Path -LiteralPath $ExistingBundle).Path
}
if ($BundleOnly) { Write-Output $bundle; exit 0 }
$version = (Get-Content -LiteralPath (Join-Path $bundle 'app\release.json') -Raw | ConvertFrom-Json).version
if (-not $Iscc) {
    $Iscc = Join-Path $env:LOCALAPPDATA 'Programs\Inno\ISCC.exe'
}
if (-not (Test-Path -LiteralPath $Iscc -PathType Leaf)) { throw 'Provide -Iscc with the installed Inno Setup 6 compiler path.' }
$dist = Join-Path $project 'dist'
New-Item -ItemType Directory -Path $dist -Force | Out-Null
& $Iscc "/DAppVersion=$version" "/DBundleRoot=$bundle" "/DInstallerOutput=$dist" (Join-Path $project 'packaging\necker.iss')
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed.' }
$installer = Join-Path $dist "Nicholas-Nice-Necker-Cube-Experiment-Setup-$version-x64.exe"
$hash = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText((Join-Path $dist 'SHA256SUMS.txt'), "$hash  $([IO.Path]::GetFileName($installer))`n")
Copy-Item -LiteralPath (Join-Path $bundle 'app\release.json') -Destination (Join-Path $dist 'release.json')
Write-Output $installer
