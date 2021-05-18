@echo off
setlocal

if exist "dist/main" (
	rmdir /s /q "dist/main"
)

call "C:\Users\Korean_Crimson\Anaconda3\Scripts\pyinstaller" --onedir --noupx --icon src/gui/media/icon.ico --exclude matplotlib --exclude pandas --exclude numpy src/main.py --noconsole

echo v| xcopy /s /v /y "src/gui/media" "dist/main/gui/media"
link.vbs "dist/LocalChat.lnk" "dist/main/main.exe"
copy "src\config.json" "dist\main"
copy "README.md" "dist"
