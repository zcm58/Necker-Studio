#define AppName "Nicholas's Nice Necker Cube Experiment"
#ifndef AppVersion
  #define AppVersion "1.3"
#endif
#ifndef AppIdGuid
  #define AppIdGuid "5FC7235D-8D03-4668-9F37-508A1B481689"
#endif
#ifndef BundleRoot
  #error BundleRoot must name the verified release bundle.
#endif
#ifndef InstallerOutput
  #define InstallerOutput "..\dist"
#endif
#ifndef PayloadList
  #error PayloadList must name the generated checked file list.
#endif
#ifndef VerifierExe
  #error VerifierExe must name the native setup verifier.
#endif

[Setup]
AppId={{{#AppIdGuid}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
AppPublisherURL=https://github.com/zcm58/Necker-Studio
AppSupportURL=https://github.com/zcm58/Necker-Studio/issues
#ifdef PatchFromVersion
DefaultDirName={code:RegisteredRoot}
DisableDirPage=yes
OutputBaseFilename=Nicholas-Nice-Necker-Cube-Experiment-Patch-{#PatchFromVersion}-to-{#AppVersion}-x64
#else
DefaultDirName={localappdata}\Programs\NicholasNiceNeckerCubeExperiment
OutputBaseFilename=Nicholas-Nice-Necker-Cube-Experiment-Setup-{#AppVersion}-x64
#endif
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#InstallerOutput}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\necker.ico
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\NeckerExperiment.exe
UninstallLogMode=append
CloseApplications=no
RestartApplications=no
AppMutex=Local\NeckerExperimentRunning
VersionInfoVersion={#AppVersion}.0.0
VersionInfoProductName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "{#VerifierExe}"; Flags: dontcopy
Source: "{#BundleRoot}\manifest.json"; DestName: "target-manifest.json"; Flags: dontcopy
#ifdef PatchFromVersion
Source: "{#SourceManifest}"; DestName: "source-manifest.json"; Flags: dontcopy
#endif
#include PayloadList
Source: "{#BundleRoot}\manifest.json"; DestDir: "{app}"; Flags: ignoreversion solidbreak

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\NeckerExperiment.exe"; WorkingDir: "{app}"; Check: ShortcutsRequested
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\NeckerExperiment.exe"; WorkingDir: "{app}"; Tasks: desktopicon; Check: ShortcutsRequested

[Run]
Filename: "{app}\NeckerExperiment.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent; Check: LaunchAllowed

[Code]
var
  VerificationFailed: Boolean;

function RegisteredRoot(Param: String): String;
begin
  Result := '';
  RegQueryStringValue(HKCU64, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{{#AppIdGuid}}_is1', 'InstallLocation', Result);
end;

function ShortcutsRequested: Boolean;
begin
  Result := Pos('/NOSHORTCUTS=1', Uppercase(GetCmdTail)) = 0;
end;

function LaunchAllowed: Boolean;
begin
  Result := (not VerificationFailed) and (Pos('/NOLAUNCH=1', Uppercase(GetCmdTail)) = 0);
end;

function NeedsFile(Relative, Hash: String): Boolean;
var
  Filename: String;
begin
  Filename := AddBackslash(ExpandConstant('{app}')) + Relative;
  Result := True;
  if FileExists(Filename) then begin
    try
      Result := Lowercase(GetSHA256OfFile(Filename)) <> Hash;
    except
      Result := True;
    end;
  end;
end;

function VerifyStage(Stage: String): Boolean;
var
  Params, SourcePath, FromVersion: String;
  ExitCode: Integer;
begin
  SourcePath := '-';
  FromVersion := '-';
#ifdef PatchFromVersion
  SourcePath := ExpandConstant('{tmp}\source-manifest.json');
  FromVersion := '{#PatchFromVersion}';
#endif
  Params := Stage + ' ' + AddQuotes(ExpandConstant('{app}')) + ' ' + AddQuotes(SourcePath) + ' ' +
    AddQuotes(ExpandConstant('{tmp}\target-manifest.json')) + ' ' + AddQuotes(FromVersion) + ' ' +
    AddQuotes('{#AppVersion}') + ' ' + AddQuotes('{{#AppIdGuid}}');
  Result := Exec(ExpandConstant('{tmp}\NeckerSetupVerifier.exe'), Params, ExpandConstant('{tmp}'),
    SW_HIDE, ewWaitUntilTerminated, ExitCode);
  if Result then Result := ExitCode = 0;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  ExtractTemporaryFile('NeckerSetupVerifier.exe');
  ExtractTemporaryFile('target-manifest.json');
#ifdef PatchFromVersion
  ExtractTemporaryFile('source-manifest.json');
#endif
  if not VerifyStage('prepare') then
    Result := 'This installation is not compatible with this package or contains modified or linked files. Close the application and use the full installer to repair or update it. No patch files were applied.';
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    VerificationFailed := True;
    try
      VerificationFailed := not VerifyStage('finish');
    except
      VerificationFailed := True;
    end;
    if VerificationFailed then
      SuppressibleMsgBox('The installed files could not be verified. Run this installer again or use the full installer to repair the application before launching it.', mbError, MB_OK, IDOK);
  end;
end;

function GetCustomSetupExitCode: Integer;
begin
  Result := 0;
  if VerificationFailed then Result := 12;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and VerificationFailed then begin
    WizardForm.FinishedHeadingLabel.Caption := 'Installation needs repair';
    WizardForm.RunList.Visible := False;
  end;
end;
