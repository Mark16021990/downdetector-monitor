import PyInstaller.__main__
import os
import shutil
import time

# Принудительное удаление папок сборки
def remove_folders():
    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Удалена папка: {folder}")
            except PermissionError as e:
                print(f"Не удалось удалить {folder}: {e}")

# Завершение процессов DowndetectorMonitor
def kill_process():
    try:
        os.system('taskkill /f /im DowndetectorMonitor.exe 2>nul')
        time.sleep(2)  # Даем время на завершение процессов
    except:
        pass

# Выполняем очистку
kill_process()
remove_folders()

# Сборка
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