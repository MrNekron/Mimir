import re

def apply_language_highlight(widget):
    """
    Подсвечивает кириллицу зеленым, а латиницу красным.
    Работает только с CTkTextbox.
    """
    if not hasattr(widget, "_textbox"):
        return
    
    target = widget._textbox

    # 1. Очищаем старую подсветку перед нанесением новой
    clear_language_highlight(widget)

    # 2. Настраиваем цвета тегов (яркие для темной темы)
    target.tag_configure("cyrillic", foreground="#2ecc71") # Зеленый (Emerald)
    target.tag_configure("latin", foreground="#e74c3c")    # Красный (Alizarin)

    content = target.get("1.0", "end-1c")
    
    # Проходим по каждой строке и каждому символу
    lines = content.split('\n')
    for line_num, line in enumerate(lines, start=1):
        for char_num, char in enumerate(line):
            idx = f"{line_num}.{char_num}"
            
            # Проверка на кириллицу (включая букву Ё)
            if re.match(r'[а-яА-ЯёЁ]', char):
                target.tag_add("cyrillic", idx)
            # Проверка на латиницу
            elif re.match(r'[a-zA-Z]', char):
                target.tag_add("latin", idx)

def clear_language_highlight(widget):
    """Удаляет всю цветовую подсветку, возвращая стандартный цвет"""
    if not hasattr(widget, "_textbox"):
        return
    target = widget._textbox
    target.tag_remove("cyrillic", "1.0", "end")
    target.tag_remove("latin", "1.0", "end")