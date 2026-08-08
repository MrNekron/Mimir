import customtkinter as ctk
from tkinter import messagebox
import os
import mods.price_smu.logic as price_logic
from mods.price_smu.bottom_gui import FileSelectionBlock
from settings.context_menu import bind_context_menu
from settings.hotkeys import handle_standard_hotkeys

class PriceSMUModeFrame(ctk.CTkFrame):
    def __init__(self, master, get_path_func, **kwargs):
        """
        get_path_func: ссылка на активный файл из основного приложения.
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        self.local_source_file = None # Файл, выбранный внутри этого режима

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        # --- 1. ВЕРХНИЙ БЛОК: Настройка категории ---
        self.top_block = ctk.CTkFrame(self.main_scroll, border_width=2, border_color="#555555")
        self.top_block.pack(pady=(50, 20), padx=25, fill="x")
        
        ctk.CTkLabel(
            self.top_block, 
            text="НАСТРОЙКА ПРАЙС СМУ", 
            font=("Roboto", 18, "bold")
        ).pack(pady=15)

        self.cat_container = ctk.CTkFrame(self.top_block, fg_color="transparent")
        self.cat_container.pack(pady=20, padx=40, fill="x")
        
        # Строка управления (Заголовок + Чекбокс)
        header_row = ctk.CTkFrame(self.cat_container, fg_color="transparent")
        header_row.pack(fill="x")
        
        ctk.CTkLabel(header_row, text="Введите категорию:", font=("Roboto", 14)).pack(side="left")
        
        # Чекбокс "По файлу"
        self.by_file_var = ctk.BooleanVar(value=False)
        self.check_by_file = ctk.CTkCheckBox(
            header_row, 
            text="По файлу", 
            variable=self.by_file_var, 
            command=self.toggle_cat_entry, 
            font=("Roboto", 12)
        )
        self.check_by_file.pack(side="left", padx=20)
        
        # Поле ввода категории
        self.f_cat = ctk.CTkEntry(
            self.cat_container, 
            width=600, 
            height=45, 
            placeholder_text="Напр: Смесители для ванны..."
        )
        self.f_cat.pack(pady=10, fill="x")
        
        # Привязываем универсальное меню ПКМ и горячие клавиши
        bind_context_menu(self.f_cat)
        self.f_cat.bind("<Control-KeyPress>", lambda e: handle_standard_hotkeys(e, self.f_cat))

        # --- 2. НИЖНИЙ БЛОК: Выбор файла характеристик ---
        self.file_block = FileSelectionBlock(self.main_scroll, self._on_file_selected)
        self.file_block.pack(pady=10, padx=25, fill="x")

        # Подсказка
        ctk.CTkLabel(
            self.main_scroll, 
            text="Результат будет сохранен в папку 'Загрузки/Прайсы СМУ'", 
            text_color="gray", 
            font=("Roboto", 11)
        ).pack(pady=10)

    def toggle_cat_entry(self):
        """Включает или выключает поле ввода в зависимости от состояния чекбокса"""
        if self.by_file_var.get():
            self.f_cat.configure(state="disabled", fg_color="#2b2b2b")
        else:
            self.f_cat.configure(state="normal", fg_color="#343638")

    def _on_file_selected(self, path):
        """Callback вызывается при выборе файла в FileSelectionBlock"""
        self.local_source_file = path

    def get_target_directory(self):
        """Находит папку Загрузки и создает в ней подпапку 'Прайсы СМУ', если её нет"""
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        target_dir = os.path.join(downloads, "Прайсы СМУ")
        
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except Exception as e:
                # В случае ошибки прав доступа возвращаем просто Загрузки
                return downloads
        return target_dir

    def _get_current_category(self):
        """Определяет категорию: либо из поля, либо из названия файла"""
        if self.by_file_var.get():
            if not self.local_source_file:
                return None
            # Извлекаем имя файла без расширения
            return os.path.splitext(os.path.basename(self.local_source_file))[0]
        else:
            return self.f_cat.get().strip()

    def save_all(self):
        """Сохранение в Excel (вызывается из main.py)"""
        if not self.local_source_file:
            messagebox.showerror("Ошибка", "Сначала выберите файл с характеристиками!")
            return None
        
        category = self._get_current_category()
        if not category:
            messagebox.showwarning("Внимание", "Не удалось определить категорию! Выберите файл или введите название.")
            return None

        # Получаем путь к целевой папке
        directory = self.get_target_directory()
        
        success, result = price_logic.run_price_smu_export(
            self.local_source_file, 
            directory, 
            category, 
            "excel"
        )
        
        if success:
            full_path, res_count = result
            messagebox.showinfo("Успех", f"Прайс СМУ готов!\nФайл: {os.path.basename(full_path)}\nСохранено в: Загрузки/Прайсы СМУ\nСтрок: {res_count}")
            return full_path
        else:
            messagebox.showerror("Ошибка", result)
            return None

    def save_all_csv(self):
        """Сохранение в CSV (вызывается из main.py)"""
        if not self.local_source_file:
            messagebox.showerror("Ошибка", "Выберите источник!")
            return None

        category = self._get_current_category()
        if not category:
            messagebox.showwarning("Внимание", "Укажите категорию!")
            return None

        directory = self.get_target_directory()
        
        success, result = price_logic.run_price_smu_export(
            self.local_source_file, 
            directory, 
            category, 
            "csv"
        )
        
        if success:
            full_path, res_count = result
            messagebox.showinfo("Успех", f"CSV сформирован!\nФайл: {os.path.basename(full_path)}\nСохранено в: Загрузки/Прайсы СМУ\nСтрок: {res_count}")
            return full_path
        else:
            messagebox.showerror("Ошибка", result)
            return None

    def rearrange(self, event=None):
        """В данном моде нет динамических плиток, перестроение не требуется"""
        pass