#define MyAppName "Go Game Now"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Savva Poliakov"
#define MyAppExeName "GGN.exe"
#define MyAppId "{{8D879A98-34CA-42FD-B03C-DEA843941C20}"
#define MyRegistryKey "Software\GGN"
#define MyDataDir "{userappdata}\GGN"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\GoGameNow
DefaultGroupName=Go Game Now
OutputBaseFilename=GGN_Setup
SetupIconFile=..\assets\logo.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\logo.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\assets\bgm.mp3"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\Go Game Now"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall Go Game Now"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Go Game Now"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Go Game Now"; Flags: nowait postinstall skipifsilent

[Code]
function GetInstalledVersion(var Version: String): Boolean;
begin
  Result := RegQueryStringValue(HKLM, '{#MyRegistryKey}', 'Version', Version);
  if not Result then
    Result := RegQueryStringValue(HKCU, '{#MyRegistryKey}', 'Version', Version);
end;

function CompareVersions(V1, V2: String): Integer;
var
  P1, P2: Integer;
  N1, N2: Integer;
begin
  Result := 0;
  while (Result = 0) and ((V1 <> '') or (V2 <> '')) do
  begin
    P1 := Pos('.', V1);
    if P1 = 0 then P1 := Length(V1) + 1;
    P2 := Pos('.', V2);
    if P2 = 0 then P2 := Length(V2) + 1;
    N1 := StrToIntDef(Copy(V1, 1, P1 - 1), 0);
    N2 := StrToIntDef(Copy(V2, 1, P2 - 1), 0);
    if N1 < N2 then Result := -1
    else if N1 > N2 then Result := 1;
    V1 := Copy(V1, P1 + 1, Length(V1));
    V2 := Copy(V2, P2 + 1, Length(V2));
  end;
end;

function InitializeSetup(): Boolean;
var
  InstalledVersion: String;
  UninstallString: String;
  ResultCode: Integer;
  Choice: Integer;
begin
  Result := True;
  if GetInstalledVersion(InstalledVersion) then
  begin
    if CompareVersions(InstalledVersion, '{#MyAppVersion}') > 0 then
    begin
      Choice := MsgBox('A newer version of Go Game Now (' + InstalledVersion + ') is already installed.' + #13#10 +
        'This installer contains version {#MyAppVersion}.' + #13#10#13#10 +
        'Click Yes to uninstall Go Game Now, or No to cancel setup.',
        mbConfirmation, MB_YESNO);
      if Choice = IDYES then
      begin
        if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'UninstallString', UninstallString) or
           RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 'UninstallString', UninstallString) then
        begin
          Exec(RemoveQuotes(UninstallString), '', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
        end;
      end;
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    RegWriteStringValue(HKLM, '{#MyRegistryKey}', 'Version', '{#MyAppVersion}');
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Choice: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if DirExists(ExpandConstant('{#MyDataDir}')) then
    begin
      Choice := MsgBox('Do you want to keep your Go Game Now save data and settings?' + #13#10 +
        'Click Yes to keep them, or No to delete them completely.',
        mbConfirmation, MB_YESNO);
      if Choice = IDNO then
        DelTree(ExpandConstant('{#MyDataDir}'), True, True, True);
    end;
    RegDeleteKeyIncludingSubkeys(HKLM, '{#MyRegistryKey}');
    RegDeleteKeyIncludingSubkeys(HKCU, '{#MyRegistryKey}');
  end;
end;
