@echo off
setlocal

::change this path as appropriate on your machine
set "pyinstaller_path=D:\Anaconda\Scripts\pyinstaller"

cd ..

if exist "dist/main" (
	rmdir /s /q "dist/main"
)

call "%pyinstaller_path%" --onedir --noupx --icon pychatter/gui/media/icon.ico --exclude matplotlib --exclude pandas --exclude numpy pychatter/__main__.py --noconsole -n pychatter

echo v| xcopy /s /v /y "pychatter/gui/media" "dist/main/gui/media"
call "tools/link.vbs" "dist/pychatter.lnk" "dist/main/main.exe"
copy "config.json" "dist"
copy "README.md" "dist"
copy "LICENSE" "dist"
