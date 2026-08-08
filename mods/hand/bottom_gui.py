import customtkinter as ctk
from tkinter import Menu
# Импорты из папки settings
from settings.context_menu import bind_context_menu
from settings.hotkeys import handle_standard_hotkeys
from settings.find_replace import open_find_replace
from settings.text_cleanup import remove_extra_spaces, remove_all_spaces

class CharacteristicBlock(ctk.CTkFrame):
    def __init__(self, master, remove_callback, drag_manager=None, global_callbacks=None):
        super().__init__(master, border_width=2, border_color="#555555", width=420)
        self.remove_callback = remove_callback

        # --- 1. ШАПКА ПОДБЛОКА (Зона захвата для Drag-and-Drop) ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=5, pady=5)
        
        self.label_title = ctk.CTkLabel(
            self.header, 
            text="ХАРАКТЕРИСТИКА", 
            font=("Roboto", 13, "bold")
        )
        self.label_title.pack(side="left", padx=10)
        
        ctk.CTkButton(
            self.header, 
            text="✕", 
            width=30, 
            height=24, 
            fg_color="#a83232", 
            hover_color="#7d2222", 
            command=self.destroy_block
        ).pack(side="right", padx=5)

        # --- 2. ПОЛЕ НАЗВАНИЯ АТРИБУТА ---
        self.entry_char = ctk.CTkEntry(
            self, 
            placeholder_text="Название атрибута", 
            width=380, 
            height=35
        )
        self.entry_char.pack(pady=5, padx=10)
        
        # Привязка меню ПКМ (с глобальными колбэками очистки)
        bind_context_menu(self.entry_char, global_callbacks=global_callbacks)
        
        # Привязка горячих клавиш
        self.entry_char.bind("<Control-KeyPress>", lambda e: handle_standard_hotkeys(
            e, self.entry_char, find_replace_func=lambda: open_find_replace(self, self.entry_char)
        ))

        # --- 3. ТЕКСТОВЫЙ БЛОК (ЗНАЧЕНИЯ) ---
        self.text_container = ctk.CTkFrame(
            self, 
            fg_color="#1d1e1e", 
            border_width=1, 
            border_color="#555555"
        )
        self.text_container.pack(pady=(5, 15), padx=10, fill="x")

        self.top_text_area = ctk.CTkFrame(self.text_container, fg_color="transparent")
        self.top_text_area.pack(fill="x")

        # Нумерация строк
        self.line_nums = ctk.CTkTextbox(
            self.top_text_area, 
            width=35, 
            height=280, 
            fg_color="transparent", 
            text_color="#777777",
            activate_scrollbars=False, 
            border_width=0, 
            wrap="none"
        )
        self.line_nums.pack(side="left", fill="y", padx=(5, 0))
        self.line_nums.insert("1.0", "1")
        self.line_nums.configure(state="disabled")

        # Поле для ввода списка значений
        self.txt_values = ctk.CTkTextbox(
            self.top_text_area, 
            height=280, 
            border_width=0, 
            fg_color="transparent",
            wrap="none", 
            activate_scrollbars=False
        )
        self.txt_values._textbox.configure(undo=True, autoseparators=True)
        self.txt_values.pack(side="left", fill="x", expand=True)

        # Скроллбары
        self.v_scrollbar = ctk.CTkScrollbar(self.top_text_area, command=self.sync_v_scroll)
        self.v_scrollbar.pack(side="right", fill="y")
        self.txt_values.configure(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = ctk.CTkScrollbar(
            self.text_container, 
            orientation="horizontal", 
            height=12, 
            command=self.txt_values.xview
        )
        self.txt_values.configure(xscrollcommand=self.h_scrollbar.set)

        # Привязка меню ПКМ для текстового поля
        bind_context_menu(
            self.txt_values, 
            on_change_callback=self.on_text_change, 
            global_callbacks=global_callbacks
        )

        # Привязка горячих клавиш для текстового поля
        self.txt_values._textbox.bind("<Control-KeyPress>", lambda e: handle_standard_hotkeys(
            e, self.txt_values, 
            find_replace_func=lambda: open_find_replace(self, self.txt_values, self.on_text_change),
            on_change_callback=self.on_text_change
        ))

        # События изменения текста
        self.txt_values.bind("<KeyRelease>", self.on_text_change)
        self.txt_values._textbox.bind("<MouseWheel>", lambda e: self.after(1, self.sync_v_scroll_from_mouse))

        # Регистрация в менеджере перетаскивания
        if drag_manager:
            drag_manager.bind_drag(self)

    # --- МЕТОДЫ ОЧИСТКИ (вызываются через GUI) ---

    def clear_block_content(self):
        """Полная очистка: и название, и значения"""
        self.entry_char.delete(0, 'end')
        self.txt_values.delete("1.0", "end")
        self.on_text_change()

    def clear_only_values(self):
        """Очистка только списка значений (название остается)"""
        self.txt_values.delete("1.0", "end")
        self.on_text_change()

    # --- ВСПОМОГАТЕЛЬНАЯ ЛОГИКА ---

    def sync_v_scroll(self, *args):
        self.txt_values.yview(*args)
        self.line_nums.yview(*args)

    def sync_v_scroll_from_mouse(self, event=None):
        fraction = self.txt_values._textbox.yview()
        self.line_nums._textbox.yview_moveto(fraction[0])

    def on_text_change(self, event=None):
        self.update_line_numbers()
        self.manage_h_scrollbar()

    def manage_h_scrollbar(self):
        self.update_idletasks()
        scroll_start, scroll_end = self.txt_values._textbox.xview()
        if scroll_start <= 0.0 and scroll_end >= 1.0:
            self.h_scrollbar.pack_forget()
        else:
            if not self.h_scrollbar.winfo_manager():
                curr_w = self.line_nums.winfo_width()
                self.h_scrollbar.pack(fill="x", padx=(curr_w + 5, 15), pady=2)

    def update_line_numbers(self):
        content = self.txt_values.get("1.0", "end-1c")
        line_count = content.count('\n') + 1
        num_digits = len(str(line_count))
        new_width = max(35, num_digits * 10 + 5)
        
        self.line_nums.configure(width=new_width)
        lines_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_nums.configure(state="normal")
        self.line_nums.delete("1.0", "end")
        self.line_nums.insert("1.0", lines_string)
        self.line_nums.configure(state="disabled")
        self.sync_v_scroll_from_mouse()

    def get_data(self):
        attr_name = self.entry_char.get().strip()
        raw_text = self.txt_values.get("1.0", "end-1c")
        values_list = [v.strip() for v in raw_text.split('\n')]
        return attr_name, values_list

    def destroy_block(self):
        self.remove_callback(self)
        self.destroy()