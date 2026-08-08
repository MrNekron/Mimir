import customtkinter as ctk
from tkinter import messagebox, Menu
import os
import mods.hand.logic as logic
from mods.hand.bottom_gui import CharacteristicBlock
from settings.drag_manager import DragManager
from settings.context_menu import bind_context_menu
from settings.hotkeys import handle_standard_hotkeys

class HandModeFrame(ctk.CTkFrame):
    def __init__(self, master, get_path_func, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.get_path = get_path_func
        self.blocks = []
        self.top_entries_containers = []
        
        # Инициализация Drag-and-Drop
        self.drag_manager = DragManager(self)
        
        self.side_margin = 25
        self.tile_spacing = 20
        self.block_fixed_width = 420

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        # --- ВЕРХНИЙ БЛОК: Данные товара ---
        self.top_block = ctk.CTkFrame(self.main_scroll, border_width=2, border_color="#555555")
        self.top_block.pack(pady=10, padx=self.side_margin, fill="x")
        
        ctk.CTkLabel(self.top_block, text="ДАННЫЕ ТОВАРА", font=("Roboto", 18, "bold")).pack(pady=10)

        self.top_grid_inner = ctk.CTkFrame(self.top_block, fg_color="transparent")
        self.top_grid_inner.pack(pady=10, padx=15, fill="x")

        # Создание полей
        self.f_art = self.create_labeled_entry("Артикул:")
        self.f_name = self.create_labeled_entry("Наименование:")
        self.f_cat1 = self.create_labeled_entry("Категория 1:")
        self.f_cat2 = self.create_labeled_entry("Категория 2:")
        self.f_cat3 = self.create_labeled_entry("Категория 3:")
        self.f_cat4 = self.create_labeled_entry("Категория 4:")
        self.f_cat5 = self.create_labeled_entry("Категория 5:")
        self.f_img = self.create_labeled_entry("Фото (ссылка):")

        # Контейнер для блоков характеристик
        self.tiles_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.tiles_container.pack(pady=20, padx=self.side_margin, fill="x")

    def create_labeled_entry(self, label_text):
        container = ctk.CTkFrame(self.top_grid_inner, fg_color="transparent")
        ctk.CTkLabel(container, text=label_text, font=("Roboto", 12)).pack(anchor="w")
        entry = ctk.CTkEntry(container, width=350, height=35)
        entry.pack(pady=(2, 0))
        
        # Привязка меню ПКМ и горячих клавиш
        bind_context_menu(entry)
        entry.bind("<Control-KeyPress>", lambda e: handle_standard_hotkeys(e, entry))
        
        self.top_entries_containers.append(container)
        return entry

    def add_new_block(self):
        new_block = CharacteristicBlock(
            self.tiles_container, 
            self.remove_block_from_list,
            drag_manager=self.drag_manager
        )
        self.blocks.append(new_block)
        self.rearrange()

    def remove_block_from_list(self, block):
        if block in self.blocks:
            self.blocks.remove(block)
            self.after(10, self.rearrange)

    def rearrange(self, event=None):
        self.update_idletasks()
        top_w = self.top_block.winfo_width()
        if top_w < 100:
            top_w = self.winfo_width() - 60
            if top_w < 100: return
            
        t_cols = max(1, top_w // 380)
        for i, container in enumerate(self.top_entries_containers):
            container.grid(row=i // t_cols, column=i % t_cols, padx=10, pady=10, sticky="nw")
            
        b_cols = max(1, int((top_w + self.tile_spacing) // (self.block_fixed_width + self.tile_spacing)))
        for i, block in enumerate(self.blocks):
            r, c = divmod(i, b_cols)
            block.grid(row=r, column=c, padx=(0, self.tile_spacing), pady=(0, self.tile_spacing), sticky="nw")

    def save_all(self):
        path = self.get_path()
        if not path: return "NEED_FILE"
        
        header_info = self._get_header_data()
        all_blocks_data = [block.get_data() for block in self.blocks]
        try:
            logic.save_matrix_to_excel(path, header_info, all_blocks_data)
            messagebox.showinfo("Успех", "Excel обновлен!")
            return path
        except Exception as e: 
            messagebox.showerror("Ошибка", str(e))
            return None

    def save_all_csv(self):
        path = self.get_path()
        if not path: return "NEED_FILE"
        
        header_info = self._get_header_data()
        all_blocks_data = [block.get_data() for block in self.blocks]
        try:
            csv_path = logic.save_matrix_to_csv(path, header_info, all_blocks_data)
            messagebox.showinfo("Успех", "CSV обновлен!")
            return csv_path
        except Exception as e: 
            messagebox.showerror("Ошибка", str(e))
            return None

    def _get_header_data(self):
        return {
            'Артикул': self.f_art.get(),
            'Наименование': self.f_name.get(),
            'Категория 1': self.f_cat1.get(),
            'Категория 2': self.f_cat2.get(),
            'Категория 3': self.f_cat3.get(),
            'Категория 4': self.f_cat4.get(),
            'Категория 5': self.f_cat5.get(),
            'Категория 6': "", 'Категория 7': "",
            'Фото': self.f_img.get()
        }