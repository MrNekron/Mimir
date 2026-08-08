import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os

class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, height=65, corner_radius=0, fg_color="#2b2b2b", **kwargs)
        
        self.callbacks = callbacks
        self.nav_buttons = []

        # --- 1. НАСТРОЙКИ ---
        self.btn_color = "#1f6aa5"    
        self.hover_color = "#144a73"  
        self.slant = 20 # Величина скоса в пикселях

        # --- 2. ИКОНКА ---
        icon_path = os.path.join(os.path.dirname(__file__), "..", "excel_icon.png")
        self.icon_img = None
        if os.path.exists(icon_path):
            try: self.icon_img = Image.open(icon_path).convert("RGBA")
            except: pass

        # --- 3. ГЕНЕРАЦИЯ ГРАФИКИ ---
        # Генерируем картинки. Левая — выступающая трапеция, Правая — вогнутая.
        self.img_exl_normal = self.render_split_button(side="left", text="EXCEL", color=self.btn_color)
        self.img_exl_hover = self.render_split_button(side="left", text="EXCEL", color=self.hover_color)
        
        self.img_csv_normal = self.render_split_button(side="right", text="CSV UTF-8", color=self.btn_color)
        self.img_csv_hover = self.render_split_button(side="right", text="CSV UTF-8", color=self.hover_color)

        # --- 4. НАВИГАЦИЯ ---
        self.mode_switch = ctk.CTkSegmentedButton(
            self, values=["Ручной", "Экспорт", "Квази", "Прайс СМУ", "Сцепка"],
            command=callbacks['change_mode']
        )
        self.mode_switch.set("Ручной")
        self.mode_switch.pack(side="left", padx=20)

        self.btn_open = ctk.CTkButton(self, text="Открыть", width=90, command=callbacks['file_open'])
        self.btn_open.pack(side="left", padx=5)
        
        self.btn_add = ctk.CTkButton(self, text="+ Характеристика", width=150, 
                                     fg_color=self.btn_color, command=callbacks['add_char'])
        self.btn_add.pack(side="left", padx=5)
        self.nav_buttons.extend([self.btn_open, self.btn_add])

        # --- 5. БЛОК СОХРАНЕНИЯ (БЕЗШОВНЫЙ СТЫК // ) ---
        self.save_area = ctk.CTkFrame(self, fg_color="transparent", width=210, height=34)
        self.save_area.pack(side="right", padx=20)

        # Сначала размещаем правую (CSV), так как левая (EXCEL) должна на нее наплывать
        self.btn_csv = ctk.CTkButton(
            self.save_area, text="", width=110, height=34,
            fg_color="transparent", hover=False, image=self.img_csv_normal,
            command=callbacks['save_csv']
        )
        # Она стоит на позиции 90 (ширина левой кнопки 110 - скос 20)
        self.btn_csv.place(x=90, y=0) 
        self.btn_csv.bind("<Enter>", lambda e: self.btn_csv.configure(image=self.img_csv_hover))
        self.btn_csv.bind("<Leave>", lambda e: self.btn_csv.configure(image=self.img_csv_normal))

        # Теперь левую (EXCEL), чтобы её хитбокс был сверху
        self.btn_excel = ctk.CTkButton(
            self.save_area, text="", width=110, height=34,
            fg_color="transparent", hover=False, image=self.img_exl_normal,
            command=callbacks['save_all']
        )
        self.btn_excel.place(x=0, y=0)
        self.btn_excel.bind("<Enter>", lambda e: self.btn_excel.configure(image=self.img_exl_hover))
        self.btn_excel.bind("<Leave>", lambda e: self.btn_excel.configure(image=self.img_exl_normal))

    def render_split_button(self, side, text, color):
        """Рисует части кнопки так, чтобы они входили друг в друга"""
        w, h = 220, 68 # 2x масштаб для четкости
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        r = 34    # Радиус круглых краев
        s = self.slant * 2 # Скос
        
        if side == "left":
            # Форма: Круг слева, Острый нос справа вверху ( / )
            # Нам нужно нарисовать до самого края w, а низ срезать на s
            points = [(r, 0), (w, 0), (w - s, h), (r, h)]
            draw.polygon(points, fill=color)
            draw.pieslice([0, 0, r*2, h], 90, 180, fill=color)
            draw.pieslice([0, h-r*2, r*2, h], 180, 270, fill=color)
            draw.rectangle([0, r, r, h-r], fill=color)
            
            # Контент
            icon_size = 36
            try: font = ImageFont.truetype("arialbd.ttf", 24)
            except: font = ImageFont.load_default()
            tw, th = draw.textbbox((0, 0), text, font=font)[2:]
            total_content_w = (icon_size + 10 + tw)
            # Центрируем Excel в его части (от 0 до w-s)
            start_x = (w - s - total_content_w) // 2 + 10
            if self.icon_img:
                icon_res = self.icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                img.paste(icon_res, (int(start_x), (h - icon_size) // 2), icon_res)
            draw.text((start_x + icon_size + 10, (h - th) // 2 - 2), text, font=font, fill="white")
            
        else:
            # Форма: Левая сторона "впадина" ( / ), правая - круглая
            # Рисуем так, чтобы левый край начинался с s вверху и 0 внизу
            points = [(s, 0), (w - r, 0), (w - r, h), (0, h)]
            draw.polygon(points, fill=color)
            draw.pieslice([w-r*2, 0, w, r*2], 270, 360, fill=color)
            draw.pieslice([w-r*2, h-r*2, w, h], 0, 90, fill=color)
            draw.rectangle([w-r, r, w, h-r], fill=color)
            
            # Текст по центру правой части
            try: font = ImageFont.truetype("arialbd.ttf", 24)
            except: font = ImageFont.load_default()
            tw, th = draw.textbbox((0, 0), text, font=font)[2:]
            # Центрируем относительно области от s до w
            text_x = s + (w - s - r - tw) // 2 + 5
            draw.text((text_x, (h - th) // 2 - 2), text, font=font, fill="white")

        return ctk.CTkImage(light_image=img, dark_image=img, size=(w//2, h//2))

    def arrange_buttons(self, is_mobile=False):
        pass