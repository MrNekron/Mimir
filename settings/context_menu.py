import customtkinter as ctk
from tkinter import Menu
from settings.find_replace import open_find_replace
from settings.text_cleanup import remove_extra_spaces, remove_all_spaces, remove_empty_lines
from settings.text_highlighter import apply_language_highlight, clear_language_highlight

def bind_context_menu(widget, on_change_callback=None, global_callbacks=None):
    """
    Привязывает универсальное меню ПКМ к любому виджету (Entry или Textbox).
    global_callbacks: словарь {'clear_all': func, 'clear_values': func} для массовой очистки.
    """
    widget.bind("<Button-3>", lambda event: _show_menu(event, widget, on_change_callback, global_callbacks))

def _show_menu(event, widget, on_change_callback, global_callbacks):
    # Создаем основное меню
    menu = Menu(widget, tearoff=0, bg="#333333", fg="white", borderwidth=0)
    
    # Определяем тип виджета и цель для команд
    is_textbox = hasattr(widget, "_textbox") and not hasattr(widget, "_entry")
    target = widget._textbox if is_textbox else widget._entry

    # --- 1. СТАНДАРТНЫЕ КОМАНДЫ ---
    menu.add_command(label="Копировать", command=lambda: target.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: _wrapper(target, "<<Paste>>", on_change_callback))
    menu.add_command(label="Вырезать", command=lambda: _wrapper(target, "<<Cut>>", on_change_callback))
    menu.add_separator()

    # --- 2. ПОДМЕНЮ: РЕГИСТР ---
    case_menu = Menu(menu, tearoff=0, bg="#333333", fg="white", borderwidth=0)
    case_menu.add_command(label="Все строчные", 
                          command=lambda: _apply_text_func(widget, str.lower, on_change_callback))
    case_menu.add_command(label="Все заглавные", 
                          command=lambda: _apply_text_func(widget, str.upper, on_change_callback))
    case_menu.add_command(label="Первая заглавная", 
                          command=lambda: _apply_text_func(widget, _capitalize_logic, on_change_callback))
    menu.add_cascade(label="Регистр", menu=case_menu)

    # --- 3. ПОДМЕНЮ: ОЧИСТКА ---
    clear_menu = Menu(menu, tearoff=0, bg="#333333", fg="white", borderwidth=0)
    clear_menu.add_command(label="Поле", command=lambda: _clear_text_logic(widget, "all", on_change_callback))
    clear_menu.add_command(label="Выделенное", command=lambda: _clear_text_logic(widget, "selection", on_change_callback))
    
    if global_callbacks:
        clear_menu.add_separator()
        if "clear_values" in global_callbacks:
            clear_menu.add_command(label="Характеристики", command=global_callbacks["clear_values"])
        if "clear_all" in global_callbacks:
            clear_menu.add_command(label="Все", command=global_callbacks["clear_all"])
    
    menu.add_cascade(label="Очистка", menu=clear_menu)

    # --- 4. ПОДМЕНЮ: РАСПОЗНОВАНИЕ RU/EN ---
    if is_textbox:
        recognize_menu = Menu(menu, tearoff=0, bg="#333333", fg="white", borderwidth=0)
        recognize_menu.add_command(label="Подсветить", command=lambda: apply_language_highlight(widget))
        recognize_menu.add_command(label="Убрать подсветку", command=lambda: clear_language_highlight(widget))
        menu.add_cascade(label="Распознование RU/EN", menu=recognize_menu)

    menu.add_separator()

    # --- 5. ПОИСК И ФОРМАТИРОВАНИЕ ---
    menu.add_command(label="Найти и заменить", 
                      command=lambda: open_find_replace(widget.master, widget, on_change_callback))
    
    menu.add_command(label="Убрать лишние пробелы", 
                      command=lambda: _apply_text_func(widget, remove_extra_spaces, on_change_callback))
    
    menu.add_command(label="Убрать все пробелы", 
                      command=lambda: _apply_text_func(widget, remove_all_spaces, on_change_callback))
    
    # Кнопка удаления пустых строк
    menu.add_command(label="Удалить пустые строки", 
                      command=lambda: _apply_text_func(widget, remove_empty_lines, on_change_callback))
    
    menu.add_separator()

    # --- 6. ВЫДЕЛИТЬ ВСЁ ---
    if is_textbox:
        menu.add_command(label="Выделить всё", command=lambda: target.tag_add("sel", "1.0", "end"))
    else:
        menu.add_command(label="Выделить всё", command=lambda: widget.select_range(0, 'end'))

    # Отображение
    menu.tk_popup(event.x_root, event.y_root)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def _wrapper(target, event_name, callback):
    """Выполняет команду (Paste/Cut) и дергает callback для обновления UI"""
    target.event_generate(event_name)
    if callback:
        target.after(10, callback)

def _apply_text_func(widget, func, callback):
    """Универсальное применение функций обработки текста к виджету"""
    is_textbox = hasattr(widget, "_textbox") and not hasattr(widget, "_entry")
    
    if is_textbox:
        content = widget.get("1.0", "end-1c")
        new_content = func(content)
        widget.delete("1.0", "end")
        widget.insert("1.0", new_content)
    else:
        content = widget.get()
        new_content = func(content)
        widget.delete(0, 'end')
        widget.insert(0, new_content)
    
    if callback:
        callback()

def _clear_text_logic(widget, mode, callback):
    """Логика очистки: либо всего поля, либо только выделенного фрагмента"""
    is_textbox = hasattr(widget, "_textbox") and not hasattr(widget, "_entry")
    target = widget._textbox if is_textbox else widget._entry
    
    try:
        if mode == "selection":
            target.delete("sel.first", "sel.last")
        else:
            if is_textbox:
                widget.delete("1.0", "end")
            else:
                widget.delete(0, 'end')
    except:
        pass # Если выделения нет, игнорируем ошибку

    if callback:
        callback()

def _capitalize_logic(text):
    """Делает первую букву заглавной для каждой строки отдельно"""
    if not text: return ""
    lines = text.split('\n')
    return "\n".join([line.strip().capitalize() for line in lines])