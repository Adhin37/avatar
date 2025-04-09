import tkinter as tk

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=35, bg="#2e2e3e", fg="#f8f8f2", hover_bg="#3e3e4e"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        
        # Create rounded rectangle button
        self.create_rounded_rect(0, 0, width, height, 10, fill=bg)
        self.create_text(width/2, height/2, text=text, fill=fg, font=("Helvetica", 10, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, e):
        self.delete("all")
        self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), 10, fill=self.hover_bg)
        self.create_text(self.winfo_width()/2, self.winfo_height()/2, 
                        text=self.itemcget(self.find_all()[-1], "text"),
                        fill="#f8f8f2", font=("Helvetica", 10, "bold"))
        
    def on_leave(self, e):
        self.delete("all")
        self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), 10, fill=self.bg)
        self.create_text(self.winfo_width()/2, self.winfo_height()/2,
                        text=self.itemcget(self.find_all()[-1], "text"),
                        fill="#f8f8f2", font=("Helvetica", 10, "bold"))
        
    def on_click(self, e):
        if self.command:
            self.command() 