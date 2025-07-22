# Building an Android APK

This guide shows how to package the **Local Modular AI Assistant** into a simple
APK using [Buildozer](https://github.com/kivy/buildozer). The APK will run the
`android_gui_app.py` Kivy interface.

## 1. Install Buildozer
Buildozer requires a Linux host with Python, Java and the Android SDK. On most
systems you can set it up with:
```bash
pip install -r android_requirements.txt
sudo apt-get install -y build-essential git python3 python3-pip openjdk-17-jdk
```
Alternatively you can use the official Buildozer Docker image.

## 2. Initialize the Buildozer project
From the project root run:
```bash
buildozer init
```
This creates a `buildozer.spec` file. Edit the following options:
- `source.include_exts = py,json`
- `requirements = python3,kivy`
- `source.main = android_gui_app.py`
- `title = LocalModularAssistant`
- `package.name = localmodularassistant`
- `package.domain = org.example`

## 3. Build the APK
Execute:
```bash
python build_apk.py
```
The resulting APK will be placed in the `bin/` directory (for example
`bin/LocalModularAssistant-0.1-debug.apk`). Install it on your device with:
```bash
adb install bin/LocalModularAssistant-0.1-debug.apk
```

This APK launches the Kivy interface that wraps the existing
`android_cli_assistant` logic, allowing the assistant to run on recent Android
versions.
