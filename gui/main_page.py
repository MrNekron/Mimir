from nicegui import ui

def render_main_page(change_page_func):
    """Витрина модулей с ярким ховером кнопки"""
    
    ui.add_head_html('''
    <style>
        .module-card {
            width: 350px;
            height: 220px;
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            background-color: #0d0d0d;
            border: 1px solid #222222;
            transition: all 0.3s ease;
        }
        .module-card:hover {
            border-color: #1f6aa5;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        }
        .card-bg {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 10% 10%, #1a1a1a 0%, #050505 100%);
            opacity: 1;
            transition: all 0.4s ease;
            z-index: 0;
        }
        .module-card:hover .card-bg {
            filter: blur(10px) brightness(0.4);
            transform: scale(1.1);
        }
        .card-content {
            position: relative;
            padding: 24px;
            height: 100%;
            display: flex;
            flex-direction: column;
            z-index: 1;
        }
        .card-title {
            color: white;
            font-size: 19px;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .card-version {
            color: #555555;
            font-size: 11px;
            font-weight: 500;
            margin-bottom: 15px;
        }
        .card-desc {
            color: #bbbbbb;
            font-size: 13px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .details-link {
            color: #1f6aa5;
            font-size: 14px;
            font-weight: 600;
            text-decoration: underline;
            text-underline-offset: 5px;
            opacity: 0;
            transform: translateY(5px);
            transition: all 0.3s ease;
            cursor: pointer;
            margin-top: 15px;
        }
        .module-card:hover .details-link {
            opacity: 1;
            transform: translateY(0);
        }

        /* --- КНОПКА ОТКРЫТЬ --- */
        .open-btn {
            position: absolute !important;
            bottom: 20px;
            right: 20px;
            background-color: #1f6aa5 !important; 
            color: #0d0d0d !important;           
            font-weight: 900 !important;
            font-size: 12px !important;
            border-radius: 4px !important;
            padding: 0 20px !important;
            height: 38px !important;
            box-shadow: none !important;
            transition: background-color 0.2s !important;
        }
        .open-btn .q-btn__content, .open-btn span {
            color: #0d0d0d !important;
        }
        /* Яркий ховер */
        .open-btn:hover {
            background-color: #3ba4f5 !important;
        }
    </style>
    ''')

    with ui.column().classes('w-full items-center gap-12'):
        ui.label('ИНСТРУМЕНТАРИЙ MIMIR').classes('text-white text-4xl font-black mt-8 tracking-tighter')

        with ui.row().classes('w-full justify-center gap-8 max-w-7xl'):
            
            def module_card(name, version, desc, target):
                with ui.element('div').classes('module-card'):
                    ui.element('div').classes('card-bg')
                    with ui.element('div').classes('card-content'):
                        ui.label(name).classes('card-title')
                        ui.label(version).classes('card-version')
                        ui.label(desc).classes('card-desc')
                        ui.label('Подробнее').classes('details-link').on('click', lambda: ui.notify(f'Информация: {name}'))
                        ui.button('ОТКРЫТЬ', on_click=lambda: change_page_func(target)) \
                            .props('unelevated') \
                            .classes('open-btn')

            module_card('РУЧНОЙ', '1.0.4', 'Классический режим наполнения товаров характеристиками вручную через плиточный интерфейс.', 'Ручной')
            module_card('КВАЗИ', '2.1.0', 'Гибридный режим с автоматической комбинаторикой характеристик и авто-заполнением строк.', 'Квази')
            module_card('ПРАЙС СМУ', '1.2.0', 'Специализированный режим для выгрузки прайсов с URL-структурой и иерархией уровней.', 'Прайс СМУ')
            module_card('СЦЕПКА', '0.8.5', 'Инструмент для мгновенного объединения множества CSV файлов в одну общую таблицу.', 'Сцепка')
            module_card('ЭКСПОРТ', '1.0.0', 'Автоматическая генерация матрицы характеристик на основе внешних Excel файлов.', 'Экспорт')