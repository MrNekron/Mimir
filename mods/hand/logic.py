import pandas as pd
import os

BASE_HEADERS = [
    'Артикул', 'Наименование',
    'Категория', 'Категория', 'Категория', 'Категория', 'Категория', 'Категория', 'Категория',
    'Цена',
    'Фото', 'Фото', 'Фото', 'Фото', 'Фото',
    '', '', '', '', '', ''
]
BASE_COLS_COUNT = len(BASE_HEADERS)

def create_new_excel(path):
    df = pd.DataFrame(columns=BASE_HEADERS)
    df.to_excel(path, index=False)

def _clean_value(value):
    """Принудительно возвращает строку и меняет точки на запятые в числах"""
    if pd.isna(value): return ""
    s = str(value).strip()
    
    # Если в строке есть точка и это похоже на число (например 1.8), меняем на 1,8
    if "." in s:
        parts = s.split('.')
        if len(parts) == 2 and parts[0].replace('-','').isdigit() and parts[1].isdigit():
            return s.replace('.', ',')
    return s

def _build_new_rows(header_data, blocks_data):
    new_rows = []
    attr_names = [attr_name for attr_name, _ in blocks_data]
    max_rows = max(len(vals) for _, vals in blocks_data) if blocks_data else 1

    for i in range(max_rows):
        sku_vals = []
        name_suffix = ""
        char_data = []

        for attr_name, values_list in blocks_data:
            # Сначала очищаем значение (заменяем точки на запятые)
            val = _clean_value(values_list[i]) if i < len(values_list) else ""
            
            char_data.append(attr_name)
            char_data.append(val)
            sku_vals.append(val)
            if val.strip(): name_suffix += f" {val.strip()}"

        sku_suffix = ";".join(sku_vals)

        row_base = [
            f"{header_data.get('Артикул', '')} {sku_suffix}".strip(),
            f"{header_data.get('Наименование', '')}{name_suffix}",
            header_data.get('Категория 1', ""),
            header_data.get('Категория 2', ""),
            header_data.get('Категория 3', ""),
            header_data.get('Категория 4', ""),
            header_data.get('Категория 5', ""),
            header_data.get('Категория 6', ""),
            header_data.get('Категория 7', ""),
            "1",
            header_data.get('Фото', ""),
            "", "", "", "", "", "", "", "", "", ""
        ]
        new_rows.append(row_base + char_data)
    return new_rows, attr_names

def _read_excel_rows(path):
    if not os.path.exists(path): return []
    try:
        df = pd.read_excel(path, header=None, dtype=str)
        rows = df.values.tolist()
        return [[_clean_value(item) for item in row] for row in rows[1:]] if rows else []
    except: return []

def _read_csv_rows(path):
    if not os.path.exists(path): return []
    try:
        df = pd.read_csv(path, sep=';', encoding='utf-8-sig', header=None, dtype=str)
        rows = df.values.tolist()
        return [[_clean_value(item) for item in row] for row in rows[1:]] if rows else []
    except: return []

def _get_existing_attr_names(rows):
    attr_names = []
    for row in rows:
        if len(row) <= BASE_COLS_COUNT: continue
        pair_count = (len(row) - BASE_COLS_COUNT + 1) // 2
        while len(attr_names) < pair_count: attr_names.append("")
        for idx in range(pair_count):
            col_idx = BASE_COLS_COUNT + idx * 2
            if col_idx < len(row):
                val = str(row[col_idx]).strip()
                if val and not attr_names[idx]: attr_names[idx] = val
    return attr_names

def _merge_attr_names(old, new):
    res = []
    for i in range(max(len(old), len(new))):
        n = new[i] if i < len(new) else ""
        o = old[i] if i < len(old) else ""
        res.append(n or o or "")
    return res

def _normalize_rows(rows, attr_names):
    final_len = BASE_COLS_COUNT + len(attr_names) * 2
    norm = []
    for row in rows:
        new_r = []
        for i in range(final_len):
            val = _clean_value(row[i]) if i < len(row) else ""
            if i >= BASE_COLS_COUNT and (i - BASE_COLS_COUNT) % 2 == 0:
                idx = (i - BASE_COLS_COUNT) // 2
                val = attr_names[idx] if idx < len(attr_names) else ""
            new_r.append(val)
        norm.append(new_r)
    return norm

def save_matrix_to_excel(path, header_data, blocks_data):
    new_rows, new_attr = _build_new_rows(header_data, blocks_data)
    old_rows = _read_excel_rows(path)
    old_attr = _get_existing_attr_names(old_rows)
    final_attr = _merge_attr_names(old_attr, new_attr)
    final_rows = _normalize_rows(old_rows + new_rows, final_attr)
    pd.DataFrame(final_rows, columns=_make_headers(len(final_attr))).to_excel(path, index=False)

def save_matrix_to_csv(path, header_data, blocks_data):
    # Если путь уже ведет к .csv, используем его как есть
    if path.lower().endswith('.csv'):
        csv_p = path
    else:
        csv_p = os.path.splitext(path)[0] + ".csv"
        
    new_rows, new_attr = _build_new_rows(header_data, blocks_data)
    
    # Пытаемся прочитать существующий CSV для слияния
    old_rows = _read_csv_rows(csv_p)
    old_attr = _get_existing_attr_names(old_rows)
    
    final_attr = _merge_attr_names(old_attr, new_attr)
    final_rows = _normalize_rows(old_rows + new_rows, final_attr)
    
    pd.DataFrame(final_rows, columns=_make_headers(len(final_attr))).to_csv(
        csv_p, index=False, sep=';', encoding='utf-8-sig'
    )
    return csv_p

def _make_headers(count):
    h = list(BASE_HEADERS)
    for _ in range(count): h.extend(["Атрибут", "Значение"])
    return h