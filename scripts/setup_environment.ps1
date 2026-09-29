param()
$ErrorActionPreference = 'Stop'
$neckerProject = Split-Path -Parent $PSScriptRoot
$neckerUv = Join-Path $neckerProject '.tools\bootstrap\bin\uv.exe'
if (-not (Test-Path -LiteralPath $neckerUv)) {
    & py -3 -m pip install --disable-pip-version-check --target (Join-Path $neckerProject '.tools\bootstrap') 'uv==0.12.21'
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the local environment manager. A working Python launcher (py) is needed.' }
}
$neckerCache = Join-Path $neckerProject '.tools\cache'
& $neckerUv python install '3.12.14' --install-dir (Join-Path $neckerProject '.python') --no-bin --no-registry --cache-dir $neckerCache
if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
$neckerBase = Join-Path $neckerProject '.python\cpython-3.12.14-windows-x86_64-none\python.exe'
$neckerVenv = Join-Path $neckerProject '.venv'
$neckerPython = Join-Path $neckerVenv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $neckerPython)) {
    & $neckerUv venv --python $neckerBase --seed $neckerVenv --cache-dir $neckerCache
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
& $neckerPython -c 'import sys; assert sys.version_info[:3] == (3,12,14), "Existing .venv must use Python 3.12.14"'
if ($LASTEXITCODE -ne 0) { throw 'The existing environment has a different Python version. It was left unchanged.' }
$neckerManifest = Get-Content -LiteralPath (Join-Path $neckerProject 'vendor\sha256.json') -Raw | ConvertFrom-Json
foreach ($neckerEntry in $neckerManifest.PSObject.Properties) {
    $neckerWheel = Join-Path $neckerProject ('vendor\' + $neckerEntry.Name)
    if ((Get-FileHash -LiteralPath $neckerWheel -Algorithm SHA256).Hash -ne $neckerEntry.Value) {
        throw "Dependency checksum mismatch: $($neckerEntry.Name)"
    }
}
Push-Location -LiteralPath $neckerProject
try {
    & $neckerUv pip sync --python $neckerPython (Join-Path $neckerProject 'requirements.txt') --cache-dir $neckerCache
    $neckerSyncExit = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($neckerSyncExit -ne 0) { throw 'Dependency installation failed.' }
& $neckerPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency verification failed.' }
Write-Output "Ready. Select $neckerPython in PyCharm and run main.py."
