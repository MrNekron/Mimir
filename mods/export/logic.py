import pandas as pd
import os

# Базовая матрица заголовков (21 колонка)
BASE_HEADERS = [
    'Артикул', 'Наименование', 
    'Категория', 'Категория', 'Категория', 'Категория', 'Категория', 'Категория', 'Категория',
    'Цена', 
    'Фото', 'Фото', 'Фото', 'Фото', 'Фото',
    '', '', '', '', '', '' 
]

def _get_consonants_prefix(text):
    """
    Генерирует префикс артикула: 
    берёт до 4-х согласных из каждого слова категории, лимит 15 символов.
    """
    if not text:
        return ""
    
    # Список согласных (русские и английские)
    consonants = "бвгджзйклмнпрстфхцчшщbcdfghjklmnpqrstvwxyz"
    words = text.split()
    res_prefix = ""
    
    for word in words:
        # Оставляем только согласные из слова
        word_consonants = [char.upper() for char in word if char.lower() in consonants]
        # Берем первые 4 согласные из этого слова
        res_prefix += "".join(word_consonants[:4])
    
    # Ограничиваем общую длину 15 символами
    return res_prefix[:15]

def _clean_value(value):
    """Очистка значений и замена точек на запятые"""
    if pd.isna(value): return ""
    s = str(value).strip()
    if "." in s:
        parts = s.split('.')
        if len(parts) == 2 and parts[0].replace('-','').isdigit() and parts[1].isdigit():
            return s.replace('.', ',')
    return s

def run_export_import(source_path, target_path, category_name, save_format="excel"):
    try:
        # 1. Загрузка структуры ИМП
        struct_file = "Структура ИМП.xlsx"
        if not os.path.exists(struct_file):
            return False, f"Файл '{struct_file}' не найден в корне проекта."
        
        df_struct = pd.read_excel(struct_file, dtype=str).fillna("")
        
        # Поиск категории в столбце A
        match = df_struct[df_struct.iloc[:, 0].str.strip() == category_name.strip()]
        if match.empty:
            return False, f"Категория '{category_name}' не найдена в файле структуры."
        
        struct_row = match.iloc[0]

        # Логика сдвига категорий (Столбцы C-G структуры это индексы 2-6)
        raw_cats = [struct_row.iloc[i] for i in range(2, 7)]
        shifted_cats = [c for c in raw_cats if str(c).strip()]
        final_cats = (shifted_cats + [""] * 7)[:7]

        # Фото из столбца H структуры (индекс 7)
        struct_photo = struct_row.iloc[7]
        
        # Генерируем "согласный" префикс артикула на основе категории
        sku_prefix = _get_consonants_prefix(category_name)

        # 2. Загрузка источника характеристик (файл, выбранный пользователем)
        df_src = pd.read_excel(source_path, header=None, dtype=str).fillna("")
        if df_src.empty: return False, "Файл-источник характеристик пуст"

        final_rows = []
        max_pairs = 0 

        for i in range(1, len(df_src)):
            row_values = df_src.iloc[i].tolist()
            if not str(row_values[0]).strip(): continue

            sku_vals = [] 
            char_data = []

            for j in range(0, len(row_values), 2):
                if j + 1 < len(row_values):
                    attr_name = _clean_value(row_values[j])
                    attr_val = _clean_value(row_values[j+1])
                    if attr_name:
                        char_data.append(attr_name)
                        char_data.append(attr_val)
                        sku_vals.append(attr_val)

            max_pairs = max(max_pairs, len(char_data) // 2)
            
            # Артикул: Префикс из категории + характеристики через ";"
            sku_suffix = ";".join(sku_vals)
            full_sku = f"{sku_prefix} {sku_suffix}".strip()
            
            # --- НАИМЕНОВАНИЕ ОСТАВЛЯЕМ ПУСТЫМ ---
            full_name = "" 

            # Сборка строки (21 базовая колонка)
            row_base = [
                full_sku,            # Артикул
                full_name,           # Наименование (Пусто)
                *final_cats,         # 7 колонок категорий со сдвигом
                "1",                 # Цена
                struct_photo,        # Фото
                "", "", "", "", "", "", "", "", "", "" 
            ]
            final_rows.append(row_base + char_data)

        if not final_rows: return False, "Данные не найдены в источнике"

        # Создание заголовков
        f_headers = list(BASE_HEADERS)
        for _ in range(max_pairs): f_headers.extend(['Атрибут', 'Значение'])
        
        df_final = pd.DataFrame([r + [""] * (len(f_headers) - len(r)) for r in final_rows], columns=f_headers)
        
        # Сохранение
        if save_format == "excel":
            if not target_path.lower().endswith('.xlsx'):
                target_path = os.path.splitext(target_path)[0] + ".xlsx"
            df_final.to_excel(target_path, index=False)
        else:
            if not target_path.lower().endswith('.csv'):
                target_path = os.path.splitext(target_path)[0] + ".csv"
            df_final.to_csv(target_path, index=False, sep=';', encoding='utf-8-sig')
            
        return True, len(final_rows)

    except Exception as e: 
        return False, f"Ошибка: {str(e)}"

def run_export_to_excel(s, t, c): return run_export_import(s, t, c, "excel")
def run_export_to_csv(s, t, c): return run_export_import(s, t, c, "csv")