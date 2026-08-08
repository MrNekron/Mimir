import customtkinter as ctk

class DragManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame  
        self.drag_block = None      
        self.start_index = None     
        
    def bind_drag(self, block):
        """Привязывает события к тем частям блока, за которые можно тащить"""
        # Тащить можно за сам блок, за хедер или за текст заголовка
        widgets = [block, block.header]
        if hasattr(block, 'label_title'):
            widgets.append(block.label_title)
        
        for w in widgets:
            w.bind("<Button-1>", lambda e, b=block: self.on_start(e, b))
            w.bind("<B1-Motion>", self.on_drag)
            w.bind("<ButtonRelease-1>", self.on_drop)

    def on_start(self, event, block):
        self.drag_block = block
        try:
            self.start_index = self.parent.blocks.index(block)
        except ValueError:
            return
        # Подсветка при захвате
        block.configure(border_color="#1f6aa5")

    def on_drag(self, event):
        if not self.drag_block: return

        # Координаты мыши относительно контейнера с плитками
        try:
            x = event.x_root - self.parent.tiles_container.winfo_rootx()
            y = event.y_root - self.parent.tiles_container.winfo_rooty()
        except: return

        for i, block in enumerate(self.parent.blocks):
            if block == self.drag_block: continue
            
            bx = block.winfo_x()
            by = block.winfo_y()
            bw = block.winfo_width()
            bh = block.winfo_height()

            # Если курсор зашел на территорию другого блока
            if bx < x < bx + bw and by < y < by + bh:
                target_index = i
                # Меняем местами в списке данных
                self.parent.blocks.pop(self.parent.blocks.index(self.drag_block))
                self.parent.blocks.insert(target_index, self.drag_block)
                # Перерисовываем сетку
                self.parent.rearrange()
                break

    def on_drop(self, event):
        if self.drag_block:
            self.drag_block.configure(border_color="#555555")
            self.drag_block = None
            self.start_index = None