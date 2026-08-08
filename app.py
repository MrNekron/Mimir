import os
import sys
from nicegui import ui

# 1. НАСТРОЙКА ПУТЕЙ
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Импорт интерфейсных компонентов
from gui.menu import render_menu
from gui.main_page import render_main_page

# Импорт модулей (GUI и логика сохранения)
from mods.scep.gui import render_scep_mode, handle_scep_save
from mods.quasi.gui import render_quasi_mode, handle_quasi_save

# --- 2. НАСТРОЙКИ СТРАНИЦЫ ---
ui.query('body').style('background-color: #1d1e1e;') 
ui.dark_mode().enable() 

# Глобальное состояние приложения
app_state = {
    'active_file': None,
    'current_page': 'Главная'
}

# --- 3. ГЛОБАЛЬНЫЕ СТИЛИ (CSS) ---
ui.add_head_html('''
<style>
    .split-btn-container { 
        display: flex; 
        height: 26px; 
        align-items: center; 
        overflow: visible !important; 
    }
    
    /* Общий стиль для кнопок сохранения (Синий фон, Темный текст) */
    .btn-split { 
        background-color: #1f6aa5 !important;
        color: #0d0d0d !important; 
        font-weight: 900 !important;
        border: none !important; 
        height: 26px !important;
        min-height: 26px !important;
        width: 115px !important;    
        font-size: 14px !important;
        cursor: pointer;
        transition: background-color 0.15s ease-in-out !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 26px !important;
        padding: 0 !important;
    }

    /* Убираем системные отступы и эффекты Quasar */
    .btn-split .q-btn__content {
        min-height: 26px !important;
        height: 26px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .btn-split .q-btn__content span {
        color: #0d0d0d !important;
        line-height: 1 !important;
    }
    .q-focus-helper, .btn-split::before { display: none !important; }

    /* Яркий ховер при наведении */
    .btn-split:hover { 
        background-color: #3ba4f5 !important; 
    }

    /* Геометрия параллельного разреза // */
    .btn-excel { 
        clip-path: polygon(0% 0%, 100% 0%, calc(100% - 12px) 100%, 0% 100%); 
        border-radius: 13px 0 0 13px !important; 
        padding-right: 6px !important; 
    }
    .btn-csv { 
        clip-path: polygon(12px 0%, 100% 0%, 100% 100%, 0% 100%); 
        border-radius: 0 13px 13px 0 !important; 
        margin-left: -11px !important; 
        padding-left: 6px !important;  
    }
</style>
''')

# --- 4. ЛОГИКА НИЖНЕЙ ПАНЕЛИ ---
def update_status(path):
    """Обновляет статусную строку в футере"""
    app_state['active_file'] = path
    if path:
        status_label.set_text(f"Активен: {os.path.basename(path)}")
        status_label.classes('text-green-400')
        btn_open_folder.set_visibility(True)
    else:
        status_label.set_text("Файл не выбран")
        status_label.classes('text-orange-400')
        btn_open_folder.set_visibility(False)

def open_active_folder():
    """Открывает папку с активным файлом в проводнике"""
    if app_state['active_file']:
        folder = os.path.dirname(app_state['active_file'])
        if os.path.exists(folder):
            os.startfile(folder)

# --- 5. ЛОГИКА НАВИГАЦИИ ---
def change_page(page_name):
    """Главный диспетчер экранов"""
    app_state['current_page'] = page_name
    content_area.clear()
    
    with content_area:
        if page_name == 'Главная':
            render_main_page(change_page)
        elif page_name == 'Сцепка':
            render_scep_mode()
        elif page_name == 'Квази':
            render_quasi_mode()
        elif page_name == 'Прайс СМУ':
            ui.label('МОДУЛЬ ПРАЙС СМУ').classes('text-white text-3xl font-black mt-10')
            ui.label('В процессе переноса...').classes('text-gray-500')
        elif page_name == 'Настройка':
            ui.label('НАСТРОЙКИ').classes('text-white text-3xl font-black mt-10')
            ui.label('Здесь будут параметры приложения.').classes('text-gray-500')
        elif page_name == 'Справка':
            ui.label('СПРАВКА').classes('text-white text-3xl font-black mt-10')
            ui.label('Руководство пользователя Mimir.').classes('text-gray-500')
        else:
            ui.label(f'Страница {page_name} скоро появится').classes('text-white mt-10')

def execute_save(format_type):
    """Диспетчер кнопок сохранения из шапки"""
    page = app_state['current_page']
    if page == 'Сцепка':
        handle_scep_save(update_status)
    elif page == 'Квази':
        handle_quasi_save(update_status, format_type)
    else:
        ui.notify(f'Для режима "{page}" сохранение ещё не настроено', type='info')

# --- 6. ИНТЕРФЕЙС ШАПКИ ---
with ui.header().classes('bg-[#2b2b2b] border-b border-[#444444] items-center justify-between px-4 py-1'):
    with ui.row().classes('items-center gap-4'):
        # Бургер-меню
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat color=white')
        ui.label('Mimir').classes('text-2xl font-black text-[#1f6aa5]')

    # Кнопки сохранения
    with ui.row().classes('items-center'):
        with ui.element('div').classes('split-btn-container'):
            ui.button('EXCEL', on_click=lambda: execute_save('excel')) \
                .props('unelevated').classes('btn-split btn-excel')
            
            ui.button('CSV UTF-8', on_click=lambda: execute_save('csv')) \
                .props('unelevated').classes('btn-split btn-csv')

# --- 7. БОКОВОЕ МЕНЮ (DRAWER) ---
left_drawer = render_menu(change_page)

# --- 8. КОНТЕНТНАЯ ОБЛАСТЬ ---
content_area = ui.column().classes('w-full p-8 items-center overflow-auto')

# --- 9. ФУТЕР (СТАТУС-БАР) ---
with ui.footer().classes('bg-[#2b2b2b] border-t border-[#444444] py-1 px-4 items-center gap-4'):
    status_label = ui.label('Файл не выбран').classes('text-orange-400 font-bold text-sm')
    
    btn_open_folder = ui.button(icon='folder', on_click=open_active_folder) \
        .props('flat round dense color=primary')
    btn_open_folder.set_visibility(False)
    
    ui.button(icon='close', on_click=lambda: update_status(None)) \
        .props('flat round dense color=red')

# --- ЗАПУСК ---
change_page('Главная')

ui.run(
    title='Mimir', 
    native=True, 
    window_size=(1300, 900), 
    storage_secret='mimir_session_secret_key_888'
)