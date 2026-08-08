def remove_extra_spaces(text):
    """
    Убирает лишние пробелы, сохраняя переносы строк:
    - Пробелы в начале и конце каждой строки.
    - Двойные пробелы внутри каждой строки -> один.
    """
    if not isinstance(text, str): return text
    # Разбиваем текст на строки, обрабатываем каждую и склеиваем обратно
    lines = text.split('\n')
    cleaned_lines = [" ".join(line.split()) for line in lines]
    return "\n".join(cleaned_lines)

def remove_all_spaces(text):
    """
    Убирает ВСЕ пробелы, но сохраняет переносы строк.
    """
    if not isinstance(text, str): return text
    # Заменяем только обычный символ пробела
    return text.replace(" ", "")

def remove_extra_spaces(text):
    """Убирает лишние пробелы внутри строк и по бокам"""
    if not isinstance(text, str): return text
    lines = text.split('\n')
    cleaned_lines = [" ".join(line.split()) for line in lines]
    return "\n".join(cleaned_lines)

def remove_all_spaces(text):
    """Убирает вообще все пробелы"""
    if not isinstance(text, str): return text
    return text.replace(" ", "")

def remove_empty_lines(text):
    """
    Удаляет строки, которые:
    - Полностью пустые
    - Содержат только невидимые символы (пробелы, табуляцию)
    """
    if not isinstance(text, str): return text
    lines = text.split('\n')
    # Оставляем только те строки, которые после strip() не стали пустыми
    cleaned_lines = [line for line in lines if line.strip()]
    return "\n".join(cleaned_lines)