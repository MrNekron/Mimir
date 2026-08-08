import customtkinter as ctk
from tkinter import filedialog
import os

class FileSelectionBlock(ctk.CTkFrame):
    def __init__(self, master, selection_callback):
        """
        master: родительский контейнер
        selection_callback: функция, которая вызывается в gui.py при выборе файла
        """
        # Синий заголовок и рамка в стиле Экспорта
        super().__init__(master, border_width=2, border_color="#1f6aa5")
        
        self.selection_callback = selection_callback
        self.source_path = None

        # Заголовок блока
        ctk.CTkLabel(
            self, 
            text="ВЫГРУЗКА ХАРАКТЕРИСТИК ДЛЯ ПРАЙСА", 
            font=("Roboto", 16, "bold")
        ).pack(pady=10)

        # Кнопка выбора файла
        self.btn_select = ctk.CTkButton(
            self, 
            text="ВЫБРАТЬ ФАЙЛ С ХАРАКТЕРИСТИКАМИ", 
            height=50, 
            font=("Roboto", 14, "bold"),
            command=self._select_file
        )
        self.btn_select.pack(pady=20, padx=30, fill="x")

        # Метка статуса выбранного файла
        self.lbl_status = ctk.CTkLabel(
            self, 
            text="Файл-источник не выбран", 
            text_color="gray"
        )
        self.lbl_status.pack(pady=(0, 20))

    def _select_file(self):
        """Открывает диалог выбора файла и передает путь родителю"""
        p = filedialog.askopenfilename(
            title="Выберите файл с характеристиками",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if p:
            self.source_path = p
            # Обновляем текст на кнопке или метку
            self.lbl_status.configure(
                text=f"Выбран: {os.path.basename(p)}", 
                text_color="#00ffaa" # Ярко-зеленый при успехе
            )
            # Передаем путь в главный GUI мода через callback
            self.selection_callback(p)

    def get_path(self):
        """Возвращает текущий выбранный путь"""
        return self.source_path