import customtkinter as ctk
from tkinter import messagebox

class FindReplaceDialog(ctk.CTkToplevel):
    def __init__(self, master, target_widget, on_change_callback=None):
        super().__init__(master)
        self.title("Найти и заменить")
        self.geometry("350x260")
        
        self.target_widget = target_widget
        self.on_change_callback = on_change_callback
        
        # Окно поверх всех
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        # Центрирование
        self.after(10, self.center_window)

        # Интерфейс
        ctk.CTkLabel(self, text="Найти:", font=("Roboto", 12)).pack(pady=(15, 0), padx=20, anchor="w")
        self.entry_find = ctk.CTkEntry(self, width=310)
        self.entry_find.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(self, text="Заменить на:", font=("Roboto", 12)).pack(padx=20, anchor="w")
        self.entry_replace = ctk.CTkEntry(self, width=310)
        self.entry_replace.pack(padx=20, pady=(0, 15))

        # Чекбокс "Только в выделении"
        self.selection_only_var = ctk.BooleanVar(value=False)
        self.check_selection = ctk.CTkCheckBox(self, text="Только в выделении", 
                                               variable=self.selection_only_var, 
                                               font=("Roboto", 12))
        self.check_selection.pack(padx=20, anchor="w", pady=(0, 15))

        self.btn_replace = ctk.CTkButton(self, text="Заменить всё", fg_color="#1f6aa5", command=self.do_replace)
        self.btn_replace.pack(pady=10)

        # Фокус на поле ввода
        self.entry_find.focus()
        self.bind("<Return>", lambda e: self.do_replace())

    def center_window(self):
        main_win = self.master.winfo_toplevel()
        x = main_win.winfo_x() + (main_win.winfo_width() // 2) - 175
        y = main_win.winfo_y() + (main_win.winfo_height() // 2) - 130
        self.geometry(f"+{x}+{y}")

    def do_replace(self):
        find_str = self.entry_find.get()
        replace_str = self.entry_replace.get()

        if not find_str:
            messagebox.showwarning("Внимание", "Введите текст для поиска")
            return

        selection_only = self.selection_only_var.get()

        # Логика для Textbox
        if isinstance(self.target_widget, ctk.CTkTextbox):
            # Проверяем, есть ли выделение
            try:
                sel_start = self.target_widget._textbox.index("sel.first")
                sel_end = self.target_widget._textbox.index("sel.last")
                has_selection = True
            except:
                has_selection = False

            if selection_only and not has_selection:
                messagebox.showwarning("Внимание", "Нет выделенного текста")
                return

            if selection_only and has_selection:
                # Заменяем только внутри выделения
                selected_text = self.target_widget._textbox.get(sel_start, sel_end)
                if find_str in selected_text:
                    new_text = selected_text.replace(find_str, replace_str)
                    self.target_widget._textbox.delete(sel_start, sel_end)
                    self.target_widget._textbox.insert(sel_start, new_text)
                else:
                    messagebox.showinfo("Результат", "Совпадений не найдено в выделенном тексте")
                    return
            else:
                # Заменяем во всем тексте
                content = self.target_widget.get("1.0", "end-1c")
                if find_str in content:
                    new_content = content.replace(find_str, replace_str)
                    self.target_widget.delete("1.0", "end")
                    self.target_widget.insert("1.0", new_content)
                else:
                    messagebox.showinfo("Результат", "Совпадений не найдено")
                    return

        # Логика для Entry
        else:
            content = self.target_widget.get()
            if find_str in content:
                new_content = content.replace(find_str, replace_str)
                self.target_widget.delete(0, 'end')
                self.target_widget.insert(0, new_content)
            else:
                messagebox.showinfo("Результат", "Совпадений не найдено")
                return

        if self.on_change_callback:
            self.on_change_callback()
        
        self.destroy()

def open_find_replace(master, target_widget, callback=None):
    FindReplaceDialog(master, target_widget, callback)