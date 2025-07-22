# Building a Standalone Windows Release

This guide explains how to package the **Local Modular AI Assistant** into a single executable using PyInstaller and then create an installer with Inno Setup.

## 1. Confirm the Main Script
The graphical interface is started by `gui_assistant.py`.

## 2. Recommended Environment
1. Create a fresh Python virtual environment (e.g. `python -m venv venv`)
2. Activate the environment and install dependencies:
   ```cmd
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Do not include the `venv/` directory when packaging.**

## 3. Example PyInstaller Command
Run PyInstaller from the project root. This bundles all modules and extra data folders (like the Vosk model and config file) into a single `.exe`:
```cmd
pyinstaller gui_assistant.py ^
  --onefile --noconfirm ^
  --add-data "modules;modules" ^
  --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" ^
  --add-data "config.json;." ^
  --add-data "assistant_memory.json;." ^
  --icon icon.ico
```
- Adjust `--icon` if you have a custom `icon.ico`. Remove the line if no icon is available.
- The `resource_path` helper in `modules/utils.py` ensures these files are accessible at runtime.

The resulting executable will be placed in the `dist/` directory (e.g. `dist\gui_assistant.exe`).

## 4. Inno Setup Script
Create a file named `installer.iss` with the following contents:
```ini
; Inno Setup script to deploy the Local Modular AI Assistant
[Setup]
AppName=Local Modular AI Assistant
AppVersion=1.0
DefaultDirName={pf}\LocalModularAIAssistant
OutputBaseFilename=LocalModularAIAssistantSetup
DisableProgramGroupPage=yes

[Files]
; Main executable
Source: "dist\gui_assistant.exe"; DestDir: "{app}"; Flags: ignoreversion
; Required data folders
Source: "dist\modules\*"; DestDir: "{app}\modules"; Flags: recursesubdirs createallsubdirs
Source: "dist\vosk-model-small-en-us-0.15\*"; DestDir: "{app}\vosk-model-small-en-us-0.15"; Flags: recursesubdirs createallsubdirs
Source: "dist\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\assistant_memory.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{desktop}\Local Modular AI Assistant"; Filename: "{app}\gui_assistant.exe"
```
The script installs the packaged files to `C:\Program Files\LocalModularAIAssistant` and adds a desktop shortcut.

## 5. Build and Test Steps
1. **Package with PyInstaller**
   - Run the PyInstaller command shown above. The `dist/` folder will contain the standalone executable and copied data folders.
2. **Create the installer**
   - Open the Inno Setup compiler and build `installer.iss`. This produces `LocalModularAIAssistantSetup.exe`.
3. **Test on a clean Windows machine**
   - Run the generated installer.
   - Verify the application launches via the desktop shortcut and that voice recognition works (Vosk model is loaded, modules are usable, etc.).

With these steps you can distribute a ready-to-run Windows installer for first-time users.
