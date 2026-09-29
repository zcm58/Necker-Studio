#define AppName "Nicholas's Nice Necker Cube Experiment"
#ifndef AppVersion
  #define AppVersion "1.0"
#endif
#ifndef BundleRoot
  #error BundleRoot must name the verified release bundle.
#endif
#ifndef InstallerOutput
  #define InstallerOutput "..\dist"
#endif

[Setup]
AppId={{5FC7235D-8D03-4668-9F37-508A1B481689}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
AppPublisherURL=https://github.com/zcm58/Necker-Studio
AppSupportURL=https://github.com/zcm58/Necker-Studio/issues
DefaultDirName={localappdata}\Programs\NicholasNiceNeckerCubeExperiment
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir={#InstallerOutput}
OutputBaseFilename=Nicholas-Nice-Necker-Cube-Experiment-Setup-{#AppVersion}-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\NeckerExperiment.exe
UninstallLogMode=append
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#AppVersion}.0.0
VersionInfoProductName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "{#BundleRoot}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\NeckerExperiment.exe"; WorkingDir: "{app}"; Check: ShortcutsRequested
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\NeckerExperiment.exe"; WorkingDir: "{app}"; Tasks: desktopicon; Check: ShortcutsRequested

[Run]
Filename: "{app}\NeckerExperiment.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
function ShortcutsRequested: Boolean;
begin
  Result := Pos('/NOSHORTCUTS=1', Uppercase(GetCmdTail)) = 0;
end;
