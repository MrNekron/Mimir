import os
from nicegui import ui, run
from . import logic as quasi_logic

# Состояние для характеристик
quasi_state = {
    'blocks': [],
    'cat_input': None,
    'combine_check': None
}

# --- ВАШ ТЕХНИЧЕСКИЙ CSS ДЛЯ ПРОБИТИЯ СТРУКТУРЫ QUASAR ---
ui.add_head_html('''
<style>
/* 1. Глобальный запрет ресайза */
textarea {
    resize: none !important;
}

/* 2. Каскадное растяжение всех слоев Quasar внутри родителя */
.force-height {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.force-height .q-field__inner,
.force-height .q-field__control,
.force-height .q-field__control-container {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
}

.force-height .q-field__native {
    flex-grow: 1 !important;
    height: 100% !important;
    min-height: 0 !important;
    padding: 10px !important;
}

/* 3. Удаление сервисной полосы Quasar снизу */
.force-height .q-field__bottom {
    display: none !important;
}
</style>
''')

def add_block():
    """Добавляет новый блок с расчетом строк"""
    max_lines = 0
    for b in quasi_state['blocks']:
        count = len(b['values'].split('\n'))
        if count > max_lines: max_lines = count
    
    initial_val = "\n" * (max_lines - 1) if max_lines > 1 else ""
    quasi_state['blocks'].append({'name': '', 'values': initial_val})
    render_quasi_mode.refresh()

def remove_block(index):
    """Удаляет блок по индексу"""
    quasi_state['blocks'].pop(index)
    render_quasi_mode.refresh()

def clear_all_blocks():
    """Полная очистка списка блоков"""
    if not quasi_state['blocks']: return
    quasi_state['blocks'] = []
    render_quasi_mode.refresh()

@ui.refreshable
def render_quasi_mode():
    """Интерфейс режима Квази"""
    with ui.column().classes('w-full items-center gap-6'):
        ui.label('ПАРАМЕТРЫ КВАЗИ-РЕЖИМА').classes('text-2xl font-bold text-white mt-4')

        # --- ТОП БЛОК ---
        with ui.card().classes('w-full max-w-5xl bg-[#2b2b2b] border border-[#555555] p-6'):
            with ui.row().classes('w-full items-center gap-6'):
                quasi_state['cat_input'] = ui.input(label='Название категории') \
                    .props('dark outlined clearable').classes('flex-1')
                
                quasi_state['combine_check'] = ui.checkbox('Комбинировать').classes('text-white')
                
                with ui.row().classes('gap-2'):
                    ui.button('➕ БЛОК', on_click=add_block).classes('bg-[#1f6aa5] text-white px-6')
                    ui.button(icon='delete', on_click=clear_all_blocks).props('flat color=red')

        # --- СЕТКА ХАРАКТЕРИСТИК (ВАША ВЕРСТКА) ---
        with ui.row().classes('w-full justify-center gap-6 wrap'):
            if not quasi_state['blocks']:
                ui.label('Список характеристик пуст.').classes('text-gray-600 mt-10 italic')
            
            for i, block in enumerate(quasi_state['blocks']):
                
                # РОДИТЕЛЬ: Жесткий CSS вместо Tailwind классов
                with ui.column().style('''
                    width: 350px;
                    height: 500px;
                    display: flex;
                    flex-direction: column;
                    background: #1d1e1e;
                    border: 2px solid #555555;
                    border-radius: 12px;
                    padding: 16px;
                    overflow: hidden;
                '''):

                    # 1. ШАПКА: Название (flex:none)
                    with ui.row().classes('w-full items-center gap-2 mb-2').style('flex: none;'):
                        ui.input(placeholder='Атрибут') \
                            .props('dark outlined dense') \
                            .classes('grow font-bold') \
                            .bind_value(quasi_state['blocks'][i], 'name')

                        ui.button(icon='close', on_click=lambda i=i: remove_block(i)) \
                            .props('flat round dense color=red')

                    # 2. КОНТЕНТ: Textarea (flex:1 и min-height:0)
                    ui.textarea() \
                        .props('dark outlined') \
                        .classes('w-full force-height text-sm') \
                        .style('flex: 1; min-height: 0; font-family: monospace;') \
                        .bind_value(quasi_state['blocks'][i], 'values')

                    # JS фикс для гарантированного удаления уголка
                    ui.timer(0.1, lambda: ui.run_javascript("""
                        document.querySelectorAll('textarea').forEach(t => {
                            t.style.resize = 'none';
                        });
                    """), once=True)

def handle_quasi_save(update_status_func, format_type):
    """Логика сохранения данных Квази"""
    category = quasi_state['cat_input'].value.strip() if quasi_state['cat_input'] else ""
    is_auto = quasi_state['combine_check'].value if quasi_state['combine_check'] else False
    
    if not category:
        ui.notify('Ошибка: Введите название категории!', type='negative')
        return
    if not quasi_state['blocks']:
        ui.notify('Ошибка: Добавьте характеристики!', type='warning')
        return

    prepared_data = [(b['name'].strip(), b['values'].split('\n')) for b in quasi_state['blocks']]
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    
    if format_type == 'excel':
        success, result = quasi_logic.save_quasi_to_excel(downloads, category, prepared_data, is_auto)
    else:
        success, result = quasi_logic.save_quasi_to_csv(downloads, category, prepared_data, is_auto)

    if success:
        full_path, count = result
        ui.notify(f'Сохранено! Строк: {count}', type='positive')
        update_status_func(full_path)
    else:
        ui.notify(str(result), type='negative')