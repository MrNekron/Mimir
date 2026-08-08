import os
import tkinter as tk
from nicegui import ui, run
from tkinter import filedialog
from . import logic as scep_logic

# Состояние модуля Сцепка
scep_state = {
    'folder': None,
    'name_field': None
}

# --- ИСПРАВЛЕННАЯ ФУНКЦИЯ ВЫБОРА ПАПКИ ---
def get_folder_path():
    """Открывает диалог выбора папки строго поверх всех окон"""
    root = tk.Tk()
    root.withdraw()  # Прячем маленькое пустое окно tkinter
    root.attributes("-topmost", True)  # Выводим на передний план
    
    # Открываем диалог, привязывая его к нашему невидимому root-окну
    folder = filedialog.askdirectory(title="Выберите папку с CSV таблицами", parent=root)
    
    root.destroy()  # Полностью закрываем временный root
    return folder

async def select_folder(label_obj):
    """Вызывает системный диалог выбора папки без разрыва соединения"""
    # Запускаем диалог в фоновом потоке через run.io_bound
    folder = await run.io_bound(get_folder_path)
    
    if folder:
        scep_state['folder'] = folder
        label_obj.set_text(f"Выбрана папка: {os.path.basename(folder)}")
        label_obj.classes('text-green-400')
    else:
        # Если выбор отменен, оставляем текущее состояние
        if not scep_state['folder']:
            label_obj.set_text("Папка не выбрана")
            label_obj.classes('text-gray-500')

def render_scep_mode():
    """Отрисовка основного экрана Сцепки"""
    with ui.column().classes('w-full max-w-3xl gap-6'):
        ui.label('СЦЕПКА CSV ТАБЛИЦ').classes('text-2xl font-bold text-white mt-4')

        # КАРТОЧКА 1: ВВОД НАЗВАНИЯ
        with ui.card().classes('w-full bg-[#2b2b2b] border border-[#555555] p-6'):
            ui.label('Название итогового файла:').classes('text-gray-300 font-bold mb-2')
            scep_state['name_field'] = ui.input(placeholder='Введите название файла') \
                .props('dark outlined cleanable') \
                .classes('w-full')

        # КАРТОЧКА 2: ВЫБОР ПАПКИ
        with ui.card().classes('w-full bg-[#2b2b2b] border border-[#1f6aa5] p-6 items-center'):
            ui.label('Выберите папку-источник').classes('text-gray-400 text-xs font-bold uppercase w-full mb-4')
            
            folder_label = ui.label('Папка не выбрана').classes('text-gray-500 mb-4')
            
            ui.button('ВЫБРАТЬ ПАПКУ С CSV', on_click=lambda: select_folder(folder_label)) \
                .classes('bg-[#1f6aa5] text-white w-full h-12 font-bold hover:bg-[#144a73]')

        # ПОДСКАЗКА
        with ui.row().classes('items-center gap-2 mt-2 opacity-50'):
            ui.icon('info', color='gray')
            ui.label("Итоговый файл будет создан в: Downloads/Mimir Сцепка").classes('text-gray-400 text-xs')

def handle_scep_save(update_status_func):
    """Запуск процесса объединения"""
    folder = scep_state['folder']
    name = scep_state['name_field'].value.strip() if scep_state['name_field'] else ""

    if not folder:
        ui.notify('Ошибка: Укажите папку с исходными файлами!', type='negative')
        return
    if not name:
        ui.notify('Ошибка: Введите название для итогового файла!', type='warning')
        return

    # Путь сохранения
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    target_dir = os.path.join(downloads, "Mimir Сцепка")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    success, result = scep_logic.run_csv_merge(folder, target_dir, name)

    if success:
        full_path, count = result
        ui.notify(f'Сцепка завершена! Объединено строк: {count}', type='positive')
        update_status_func(full_path)
    else:
        ui.notify(str(result), type='negative')