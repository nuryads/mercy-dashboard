@echo off
cd /d "%~dp0"
where blender >nul 2>nul
if errorlevel 1 (
 echo Blender belum ada di PATH. Install Blender resmi dahulu: https://www.blender.org/download/
 pause
 exit /b 1
)
blender --background --python blender\build_blend.py -- "%CD%"
if errorlevel 1 (echo Gagal membuat file BLEND & pause & exit /b 1)
echo Selesai: MERCY_Factory_World.blend
pause
