import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import os
import mods.export.logic as export_logic

class ExportModeFrame(ctk.CTkFrame):
    def __init__(self, master, get_path_func, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.get_path = get_path_func
        self.source_file = None

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        # --- ЦЕНТРАЛЬНЫЙ БЛОК КАТЕГОРИИ ---
        self.top_block = ctk.CTkFrame(self.main_scroll, border_width=2, border_color="#555555")
        self.top_block.pack(pady=20, padx=25, fill="x")
        
        ctk.CTkLabel(self.top_block, text="НАСТРОЙКА ЭКСПОРТА", font=("Roboto", 18, "bold")).pack(pady=15)

        self.cat_container = ctk.CTkFrame(self.top_block, fg_color="transparent")
        self.cat_container.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(self.cat_container, text="Введите категорию (для поиска в структуре):", font=("Roboto", 14)).pack(anchor="w")
        self.f_cat = ctk.CTkEntry(self.cat_container, width=600, height=45, placeholder_text="Например: Смартфоны...")
        self.f_cat.pack(pady=10, fill="x")
        self.setup_entry_hotkeys(self.f_cat)

        # --- БЛОК ВЫБОРА ФАЙЛА ---
        self.bottom_block = ctk.CTkFrame(self.main_scroll, border_width=2, border_color="#1f6aa5")
        self.bottom_block.pack(pady=10, padx=25, fill="x")

        self.btn_select_src = ctk.CTkButton(self.bottom_block, text="ВЫБРАТЬ ФАЙЛ С ХАРАКТЕРИСТИКАМИ (EXCEL)", 
                                            height=50, font=("Roboto", 14, "bold"), command=self.select_source)
        self.btn_select_src.pack(pady=25, padx=30, fill="x")
        
        self.lbl_src = ctk.CTkLabel(self.bottom_block, text="Файл-источник не выбран", text_color="gray")
        self.lbl_src.pack(pady=(0, 20))

    def setup_entry_hotkeys(self, widget):
        widget.bind("<Control-KeyPress>", lambda e: self.handle_entry_keys(e, widget))
        menu = Menu(widget, tearoff=0, bg="#333333", fg="white", borderwidth=0)
        menu.add_command(label="Вставить", command=lambda: widget.focus_get().event_generate("<<Paste>>"))
        menu.add_command(label="Копировать", command=lambda: widget.focus_get().event_generate("<<Copy>>"))
        menu.add_separator()
        menu.add_command(label="Выделить всё", command=lambda: widget.select_range(0, 'end'))
        widget.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

    def handle_entry_keys(self, event, widget):
        code = event.keycode
        if code == 65: widget.select_range(0, 'end'); return "break"
        if code == 67: widget.focus_get().event_generate("<<Copy>>"); return "break"
        if code == 86: widget.focus_get().event_generate("<<Paste>>"); return "break"

    def select_source(self):
        p = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if p:
            self.source_file = p
            self.lbl_src.configure(text=f"Выбран файл: {os.path.basename(p)}", text_color="#00ffaa")

    def save_all(self):
        target = self.get_path()
        if not self.source_file or not target:
            messagebox.showerror("Ошибка", "Выберите источник и укажите файл сохранения!")
            return
        
        success, res = export_logic.run_export_to_excel(self.source_file, target, self.f_cat.get())
        if success: messagebox.showinfo("Успех", f"Импорт завершен! Строк: {res}")
        else: messagebox.showerror("Ошибка", res)

    def save_all_csv(self):
        target = self.get_path()
        if not self.source_file or not target:
            messagebox.showerror("Ошибка", "Выберите источник и укажите файл сохранения!")
            return

        success, res = export_logic.run_export_to_csv(self.source_file, target, self.f_cat.get())
        if success: messagebox.showinfo("Успех", f"Импорт завершен! Строк: {res}")
        else: messagebox.showerror("Ошибка", res)

    def rearrange(self, event=None):
        pass # В этом моде теперь всего одно поле, перестраивать нечего