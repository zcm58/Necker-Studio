param(
    [switch]$BundleOnly,
    [string]$ExistingBundle = '',
    [string]$BaselineBundle = '',
    [string]$BaselineManifestSha256 = '',
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
if (-not $Iscc) { $Iscc = Join-Path $env:LOCALAPPDATA 'Programs\Inno\ISCC.exe' }
if (-not (Test-Path -LiteralPath $Iscc -PathType Leaf)) { throw 'Provide -Iscc with the installed Inno Setup 6 compiler path.' }
$dist = Join-Path $project 'dist'
New-Item -ItemType Directory -Path $dist -Force | Out-Null
$buildRoot = Split-Path -Parent $bundle
$verifier = Join-Path $buildRoot 'NeckerSetupVerifier.exe'
$full = Join-Path $buildRoot 'full'
& $python (Join-Path $PSScriptRoot 'build_patch.py') --bundle $bundle --output $full
if ($LASTEXITCODE -ne 0) { throw 'Full inventory preparation failed.' }
$defines = @("/DAppVersion=$version", "/DBundleRoot=$bundle", "/DInstallerOutput=$dist", "/DVerifierExe=$verifier")
& $Iscc @defines "/DPayloadList=$(Join-Path $full 'payload.iss')" (Join-Path $project 'packaging\necker.iss')
if ($LASTEXITCODE -ne 0) { throw 'Inno full installer compilation failed.' }
$patchRecords = @()
if ($BaselineBundle) {
    $baseline = (Resolve-Path -LiteralPath $BaselineBundle).Path
    $sourceManifest = Join-Path $baseline 'manifest.json'
    $fromVersion = (Get-Content -LiteralPath (Join-Path $baseline 'app\release.json') -Raw | ConvertFrom-Json).version
    $patchBuild = Join-Path $buildRoot "patch-$fromVersion"
    & $python (Join-Path $PSScriptRoot 'build_patch.py') --bundle $bundle --output $patchBuild --baseline $sourceManifest --baseline-sha256 $BaselineManifestSha256 --from-version $fromVersion
    if ($LASTEXITCODE -ne 0) { throw 'Patch preparation failed.' }
    & $Iscc @defines "/DPatchFromVersion=$fromVersion" "/DSourceManifest=$sourceManifest" "/DPayloadList=$(Join-Path $patchBuild 'payload.iss')" (Join-Path $project 'packaging\necker.iss')
    if ($LASTEXITCODE -ne 0) { throw 'Inno patch compilation failed.' }
    $patchRecords += (Join-Path $patchBuild 'build.json')
}
& $python (Join-Path $PSScriptRoot 'build_patch.py') --finalize --dist $dist --version $version --records @patchRecords
if ($LASTEXITCODE -ne 0) { throw 'Release metadata generation failed.' }
Copy-Item -LiteralPath (Join-Path $bundle 'app\release.json') -Destination (Join-Path $dist 'release.json')
Write-Output (Join-Path $dist "Nicholas-Nice-Necker-Cube-Experiment-Setup-$version-x64.exe")
