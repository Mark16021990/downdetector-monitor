import PyInstaller.__main__
import os

# Очистка предыдущих сборок
if os.path.exists('build'):
    os.system('rmdir /s /q build')
if os.path.exists('dist'):
    os.system('rmdir /s /q dist')

PyInstaller.__main__.run([
    'src/gui_app.py',
    '--onefile',
    '--windowed',
    '--name=DowndetectorMonitor',
    '--add-data=config.ini;.',
    '--hidden-import=requests',
    '--hidden-import=plyer',
    '--hidden-import=configparser',
    '--hidden-import=logging',
    '--hidden-import=threading',
    '--hidden-import=urllib.parse',
    '--hidden-import=tkinter',
    '--hidden-import=PIL',
    '--hidden-import=matplotlib',
    '--hidden-import=matplotlib.backends.backend_tkagg',
])