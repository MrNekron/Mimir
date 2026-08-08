from nicegui import ui

def render_menu(change_page_func):
    """
    Рисует боковое меню.
    change_page_func: ссылка на функцию смены страницы из app.py
    """
    # Стили для элементов навигации
    ui.add_head_html('''
    <style>
        .nav-item {
            width: 100%;
            padding: 15px 0;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: #888888;
        }
        .nav-item:hover {
            background-color: #2b2b2b;
            color: #1f6aa5;
        }
        .nav-label {
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
    </style>
    ''')

    # Создаем боковую панель (Drawer)
    with ui.left_drawer(value=True, fixed=True).classes('bg-[#1d1e1e] border-r border-[#333333] p-0 overflow-hidden') \
        .props('width=85 breakpoint=0') as drawer:
        
        with ui.column().classes('w-full items-center gap-0'):
            
            # Вспомогательная функция для генерации кнопок
            def nav_btn(icon, label, target):
                with ui.element('div').classes('nav-item').on('click', lambda: change_page_func(target)):
                    ui.icon(icon).classes('text-2xl')
                    ui.label(label).classes('nav-label')

            # Список кнопок навигации
            nav_btn('home', 'Главная', 'Главная')
            nav_btn('extension', 'ИМП', 'Квази')
            nav_btn('assignment', 'СМУ', 'Прайс СМУ')
            nav_btn('settings', 'Настройка', 'Настройка')
            nav_btn('help', 'Справка', 'Справка')
            
    return drawer