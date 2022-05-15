@echo off
setlocal

::change this path as appropriate on your machine
set "pyinstaller_path=D:\Anaconda\Scripts\pyinstaller"

cd ..

if exist "dist/main" (
	rmdir /s /q "dist/main"
)

call "%pyinstaller_path%" --onedir --noupx --icon localchat/gui/media/icon.ico --exclude matplotlib --exclude pandas --exclude numpy localchat/__main__.py --noconsole -n LocalChat

echo v| xcopy /s /v /y "localchat/gui/media" "dist/main/gui/media"
call "tools/link.vbs" "dist/LocalChat.lnk" "dist/main/main.exe"
copy "config.json" "dist"
copy "README.md" "dist"
copy "LICENSE" "dist"
