; Inno Setup script template for MedBIS Price Intelligence.
; Build the EXE first with scripts\build_exe.ps1, then compile this script in Inno Setup.

#define MyAppName "MedBIS Price Intelligence"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "MedBIS"
#define MyAppExeName "MedBIS Price Intelligence.exe"

[Setup]
AppId={{8A00B8AC-0890-4B86-B894-34E8D82A1175}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist-installer
OutputBaseFilename=MedBIS-Price-Intelligence-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

