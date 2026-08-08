import pandas as pd
import os
import re

def _get_safe_filename(name):
    """Очищает название для использования в качестве имени файла Windows"""
    if not name: return "merged_data"
    safe_name = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return safe_name

def run_csv_merge(source_folder, target_dir, output_name):
    """
    Объединяет все CSV в папке в один файл.
    1-21 (A-U): Базовые заголовки.
    22+ (V...): Цикл Атрибут | Значение | Атрибут | Значение.
    """
    try:
        # 1. Список файлов
        all_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.csv')]
        if not all_files:
            return False, "В выбранной папке нет CSV файлов."

        filename = _get_safe_filename(output_name) + ".csv"
        target_path = os.path.join(target_dir, filename)

        all_data_rows = []
        max_cols_found = 0

        # 2. Сбор данных (без заголовков исходных файлов)
        for file in all_files:
            file_path = os.path.join(source_folder, file)
            try:
                df = pd.read_csv(
                    file_path, 
                    sep=';', 
                    encoding='utf-8-sig', 
                    header=None, 
                    dtype=str
                ).fillna("")
                
                rows = df.values.tolist()
                if not rows: continue

                # Отрезаем первую строку каждого файла (заголовок)
                data_part = rows[1:]
                
                for r in data_part:
                    all_data_rows.append(r)
                    if len(r) > max_cols_found:
                        max_cols_found = len(r)
            except Exception as e:
                print(f"Ошибка чтения {file}: {e}")
                continue

        if not all_data_rows:
            return False, "Данные для объединения не найдены."

        # 3. ФОРМИРУЕМ ЭТАЛОННЫЙ ЗАГОЛОВОК
        # Базовая часть: 21 столбец (от A до U)
        base_headers = [
            'Артикул',       # 1 (A)
            'Наименование',  # 2 (B)
            'Категория',     # 3 (C)
            'Категория',     # 4 (D)
            'Категория',     # 5 (E)
            'Категория',     # 6 (F)
            'Категория',     # 7 (G)
            'Категория',     # 8 (H)
            'Категория',     # 9 (I)
            'Цена',          # 10 (J)
            'Фото',          # 11 (K)
            'Фото',          # 12 (L)
            'Фото',          # 13 (M)
            'Фото',          # 14 (N)
            'Фото',          # 15 (O)
            '',              # 16 (P)
            '',              # 17 (Q)
            '',              # 18 (R)
            '',              # 19 (S)
            '',              # 20 (T)
            ''               # 21 (U)
        ]
        
        final_headers = list(base_headers)

        # 4. ДОБАВЛЯЕМ ЦИКЛ АТРИБУТ/ЗНАЧЕНИЕ (начиная с 22-го столбца - V)
        # Цикл продолжается, пока не покроем всю ширину данных
        while len(final_headers) < max_cols_found:
            final_headers.append("Атрибут") # Будет на 22, 24, 26... местах
            final_headers.append("Значение") # Будет на 23, 25, 27... местах

        # Уточняем финальную ширину
        total_width = max(len(final_headers), max_cols_found)
        final_headers = final_headers[:total_width]

        # 5. НОРМАЛИЗАЦИЯ (выравнивание всех строк по ширине заголовка)
        normalized_data = []
        for r in all_data_rows:
            if len(r) < total_width:
                r.extend([""] * (total_width - len(r)))
            else:
                r = r[:total_width]
            normalized_data.append(r)

        # 6. СБОРКА И СОХРАНЕНИЕ
        final_table = [final_headers] + normalized_data
        df_result = pd.DataFrame(final_table)

        try:
            df_result.to_csv(
                target_path, 
                index=False, 
                sep=';', 
                encoding='utf-8-sig', 
                header=False
            )
        except PermissionError:
            return False, "Для продолжения закройте итоговый файл CSV =)"

        return True, (target_path, len(normalized_data))

    except Exception as e:
        return False, f"Ошибка в логике сцепки: {str(e)}"