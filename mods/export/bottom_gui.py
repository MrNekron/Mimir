import customtkinter as ctk
from tkinter import messagebox

# Указываем путь к логике
from mods.hand import logic

class CharacteristicBlock(ctk.CTkFrame):
    def __init__(self, master, remove_callback):
        # Фиксированная ширина (420px) позволяет блокам выстраиваться в ряд (плитку)
        super().__init__(master, border_width=2, border_color="#555555", width=420)
        
        self.remove_callback = remove_callback

        # --- 1. ШАПКА ПОДБЛОКА ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=5, pady=5)
        
        self.label_title = ctk.CTkLabel(self.header, text="ХАРАКТЕРИСТИКА", font=("Roboto", 13, "bold"))
        self.label_title.pack(side="left", padx=10)
        
        # Кнопка удаления блока (крестик)
        self.btn_delete = ctk.CTkButton(self.header, text="✕", width=30, height=24, 
                                        fg_color="#a83232", hover_color="#7d2222",
                                        command=self.destroy_block)
        self.btn_delete.pack(side="right", padx=5)

        # --- 2. ПОЛЕ НАЗВАНИЯ АТРИБУТА ---
        # Например: Цвет, Размер, Материал
        self.entry_char = ctk.CTkEntry(self, placeholder_text="Название атрибута (напр. Цвет)", width=380, height=35)
        self.entry_char.pack(pady=5, padx=10)

        # Подпись для текстового поля
        self.label_hint = ctk.CTkLabel(self, text="Значения (каждое с новой строки):", font=("Roboto", 11))
        self.label_hint.pack(pady=(5, 0), anchor="w", padx=15)

        # --- 3. ПОЛЕ ЗНАЧЕНИЙ (МНОГОСТРОЧНОЕ) ---
        # Высота 300px согласно ТЗ
        self.txt_values = ctk.CTkTextbox(self, width=380, height=300, border_width=1, border_color="#555555")
        self.txt_values.pack(pady=5, padx=10)

    def get_data(self):
        """
        Собирает данные из этого блока.
        Возвращает кортеж: (Название_Атрибута, [Список_Значений])
        """
        attr_name = self.entry_char.get().strip()
        
        # Получаем весь текст, разбиваем на строки
        raw_text = self.txt_values.get("1.0", "end-1c")
        # Очищаем строки от лишних пробелов и исключаем пустые строки
        values_list = [v.strip() for v in raw_text.split('\n') if v.strip()]
        
        return attr_name, values_list

    def destroy_block(self):
        """
        Метод удаления блока.
        Вызывает callback из главного окна, чтобы тот убрал блок из своего списка,
        а затем физически уничтожает виджет.
        """
        self.remove_callback(self)
        self.destroy()