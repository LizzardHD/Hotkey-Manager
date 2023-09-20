import tkinter as tk
from tkinter import ttk

class Tooltip:
    def __init__(self, widget, get_tooltip_text):
        self.widget = widget
        self.get_tooltip_text = get_tooltip_text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.get_tooltip_text())
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

root = tk.Tk()
root.title("OptionMenu with Dynamic Tooltip")

option_var = tk.StringVar()
options = ["Item 1", "Item 2", "Item 3"]
options_tips = {"Item 1": "Info 1", "Item 2": "Info 2", "Item 3": "Info 3"}

option_menu = ttk.OptionMenu(root, option_var, options[0], *options)
option_menu.pack(padx=10, pady=10)

def get_tooltip_text():
    return options_tips.get(option_var.get(), "")

tooltip = Tooltip(option_menu, get_tooltip_text)

root.mainloop()
