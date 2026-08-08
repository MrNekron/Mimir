import pandas as pd
import os
import re

def _get_project_root():
    """Находит путь к корневой папке проекта (где лежит main.py)"""
    # mods/price_smu/logic.py -> вверх на 2 уровня до корня
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def _get_safe_filename(name):
    """Очищает название для использования в имени файла Windows"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def _get_consonants_prefix(text):
    """Генерация префикса артикула: до 4 согласных из каждого слова, лимит 15 символов"""
    if not text: return ""
    consonants = "бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxyz"
    words = text.split()
    res_prefix = ""
    for word in words:
        # Извлекаем согласные из текущего слова
        word_consonants = [char.upper() for char in word if char.lower() in consonants]
        # Берем первые 4 согласные слова
        res_prefix += "".join(word_consonants[:4])
    return res_prefix[:15]

def _clean_value(value):
    """
    Преобразует точки в запятые только в чисто числовых значениях (напр. 1.2 -> 1,2).
    Если в значении есть буквы (напр. А12.3), оставляет как есть.
    """
    if pd.isna(value): return ""
    s = str(value).strip()
    
    if "." in s:
        parts = s.split('.')
        # Проверяем, что в строке ровно одна точка
        if len(parts) == 2:
            p1 = parts[0].replace('-', '') # Убираем минус для проверки на число
            p2 = parts[1]
            
            # Если обе части состоят только из цифр (или одна из них пустая, напр. .5)
            if (p1.isdigit() or p1 == "") and (p2.isdigit() or p2 == ""):
                if p1 or p2: # Защита от одиночной точки
                    return s.replace('.', ',')
    
    return s

def run_price_smu_export(source_path, target_dir, category_name, save_format="excel"):
    """
    Основная логика экспорта Прайс СМУ.
    """
    try:
        # 1. ПУТИ И ИМЕНА
        ext = ".xlsx" if save_format == "excel" else ".csv"
        filename = _get_safe_filename(category_name) + ext
        target_path = os.path.join(target_dir, filename)

        # 2. ЗАГРУЗКА СТРУКТУРЫ СМУ И ПОИСК ДАННЫХ
        root = _get_project_root()
        struct_file = os.path.join(root, "Структура СМУ.xlsx")
        
        if not os.path.exists(struct_file):
            return False, f"Файл структуры не найден в корне: {struct_file}"

        # Читаем структуру БЕЗ заголовков (A=0, B=1...)
        df_struct = pd.read_excel(struct_file, header=None, dtype=str).fillna("")
        
        found_struct_row = None
        # Ищем категорию в столбце B (индекс 1)
        for i in range(len(df_struct)):
            if str(df_struct.iloc[i, 1]).strip().lower() == category_name.strip().lower():
                found_struct_row = df_struct.iloc[i]
                break
        
        if found_struct_row is None:
            return False, f'Категория "{category_name}" не найдена в Структуре СМУ'

        # URL категории берем из столбца A (индекс 0)
        url_val = str(found_struct_row.iloc[0]).strip()
        
        # Уровни C-G (индексы 2-6) со сдвигом влево
        levels_data = []
        for i in range(2, 7):
            val = str(found_struct_row.iloc[i]).strip()
            if val and val.lower() != "nan":
                levels_data.append(val)
        
        # ОПРЕДЕЛЕНИЕ ЕДИНИЦЫ ИЗМЕРЕНИЯ
        unit_val = "шт"
        if levels_data and levels_data[0] == "Крепеж и метизы":
            unit_val = "кг"

        level_headers = [f"Уровень {i+1}" for i in range(len(levels_data))]

        # 3. ЗАГРУЗКА ИСТОЧНИКА ДАННЫХ
        df_src = pd.read_excel(source_path, header=None, dtype=str).fillna("")
        if df_src.empty:
            return False, "Выбранный файл-источник пуст."

        final_rows = []
        char_headers_global = [] # Заголовки свойств
        sku_prefix = _get_consonants_prefix(category_name)

        # 4. ОБРАБОТКА СТРОК ИСТОЧНИКА (начиная со 2-й строки - индекс 1)
        for i in range(1, len(df_src)):
            row_raw = df_src.iloc[i].tolist()
            # Пропускаем строку, если она пустая
            if not any(str(x).strip() for x in row_raw): continue

            current_row_attr_names = []  # Имена свойств (из A, C, E...)
            current_row_attr_values = [] # Значения свойств (из B, D, F...)
            sku_vals = []

            # Извлекаем характеристики парами из этой же строки
            for j in range(0, len(row_raw), 2):
                if j + 1 < len(row_raw):
                    attr_name = _clean_value(row_raw[j])
                    attr_val = _clean_value(row_raw[j+1])
                    
                    if attr_name:
                        current_row_attr_names.append(attr_name)
                        current_row_attr_values.append(attr_val)
                        if attr_val: sku_vals.append(attr_val)

            # Сохраняем имена атрибутов из первой строки данных как заголовки
            if not char_headers_global:
                char_headers_global = current_row_attr_names

            # Собираем Артикул: Префикс + суффикс из значений через ;
            full_sku = f"{sku_prefix} {';'.join(sku_vals)}".strip()

            # Сборка строки по шаблону
            # Артикул | URL | Уровни... | Название("") | | шт/кг | 1 | 10 | | Характеристики...
            row_data = (
                [full_sku, url_val] + 
                levels_data + 
                ["", "|", unit_val, "1", "10", "|"] + 
                current_row_attr_values
            )
            final_rows.append(row_data)

        if not final_rows:
            return False, "Данные не найдены."

        # 5. ФОРМИРОВАНИЕ ИТОГОВЫХ ЗАГОЛОВКОВ ТАБЛИЦЫ
        final_headers = (
            ["Артикул", "URL категории"] + 
            level_headers + 
            ["Название", "|", "Ед. изм.", "Цена", "Точность", "|"] + 
            char_headers_global
        )

        # 6. СОХРАНЕНИЕ
        max_cols = len(final_headers)
        normalized_rows = [r + [""] * (max_cols - len(r)) for r in final_rows]

        df_final = pd.DataFrame(normalized_rows, columns=final_headers)
        
        try:
            if save_format == "excel":
                df_final.to_excel(target_path, index=False)
            else:
                df_final.to_csv(target_path, index=False, sep=';', encoding='utf-8-sig')
        except PermissionError:
            return False, "Для продолжения закройте файл Excel =)"

        return True, (target_path, len(final_rows))

    except Exception as e:
        return False, f"Ошибка Logic: {str(e)}"