<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
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

        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def on_option_selected(event):
    selected_item = option_var.get()
    # You can perform actions based on the selected item here

root = tk.Tk()
root.title("OptionMenu with Tooltip")

option_var = tk.StringVar()

options = ["Item 1", "Item 2", "Item 3"]
option_menu = ttk.OptionMenu(root, option_var, options[0], *options, command=on_option_selected)
option_menu.pack(padx=10, pady=10)

# Create tooltips for each item in the OptionMenu
tooltips = [Tooltip(option_menu, item) for item in options]

root.mainloop()
=======
import tkinter as tk
from tkinter import ttk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
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

        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def on_option_selected(event):
    selected_item = option_var.get()
    # You can perform actions based on the selected item here

root = tk.Tk()
root.title("OptionMenu with Tooltip")

option_var = tk.StringVar()

options = ["Item 1", "Item 2", "Item 3"]
option_menu = ttk.OptionMenu(root, option_var, options[0], *options, command=on_option_selected)
option_menu.pack(padx=10, pady=10)

# Create tooltips for each item in the OptionMenu
tooltips = [Tooltip(option_menu, item) for item in options]

root.mainloop()
>>>>>>> 3204b55c2e697d0d73acd234189f1afccf19898d
