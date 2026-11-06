; DuoAI per-user Windows installer
#define MyAppName "DuoAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DuoAI"
#define MyAppExeName "DuoAI.exe"

[Setup]
AppId={{A1C8D2F0-7E6B-4B4B-8B73-1A1E8E6D4F21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\DuoAI
DefaultGroupName={#MyAppName}
OutputDir=dist-installer
OutputBaseFilename=DuoAI-Setup-{#MyAppVersion}
Compression=lzma2/fast
SolidCompression=no
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Files]
Source: "dist\DuoAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\DuoAI"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DuoAI"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DuoAI"; Flags: postinstall nowait skipifsilent
