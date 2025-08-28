import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/gui_app.py',
    '--onefile',
    '--windowed',
    '--name=DowndetectorMonitor',
    '--add-data=config.ini;.',
])