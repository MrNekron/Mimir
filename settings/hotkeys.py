import customtkinter as ctk

KEYS = {
    'A': 65, # Ф
    'C': 67, # С
    'V': 86, # М
    'X': 88, # Ч
    'Z': 90, # Я
    'F': 70, # А
}

def handle_standard_hotkeys(event, widget, find_replace_func=None, on_change_callback=None):
    code = event.keycode
    ctrl = (event.state & 0x4) != 0

    if not ctrl:
        return None

    # Находим внутренний виджет (Tkinter), так как события <<Copy>> и т.д. 
    # работают надежно только на нем.
    if hasattr(widget, "_textbox"):
        target = widget._textbox
    elif hasattr(widget, "_entry"):
        target = widget._entry
    else:
        target = widget

    # Выделить всё
    if code == KEYS['A']:
        if isinstance(widget, ctk.CTkTextbox):
            target.tag_add("sel", "1.0", "end")
        else:
            widget.select_range(0, 'end')
        return "break"

    # Копировать
    if code == KEYS['C']:
        target.event_generate("<<Copy>>")
        return "break"

    # Вставить
    if code == KEYS['V']:
        target.event_generate("<<Paste>>")
        if on_change_callback:
            widget.after(20, on_change_callback)
        return "break"

    # Вырезать
    if code == KEYS['X']:
        target.event_generate("<<Cut>>")
        if on_change_callback:
            widget.after(20, on_change_callback)
        return "break"

    # Отмена (Ctrl+Z)
    if code == KEYS['Z']:
        try:
            target.event_generate("<<Undo>>")
            if on_change_callback:
                widget.after(20, on_change_callback)
        except:
            pass
        return "break"

    # Поиск
    if code == KEYS['F'] and find_replace_func:
        find_replace_func()
        return "break"

    return None