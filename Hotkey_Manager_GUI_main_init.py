
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import font as tkfont
import json
import threading
import keyboard
import mouse
import time
import re
import textwrap

'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Hotkey Class:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
class Hotkey_Loop:
    def __init__(self):
        # Variables for starting and stopping the Hotkey
        self.programm_running = False
        self.loop_running = False
        self.falling_trigger = False
        # Time Variables
        self.start_time = False
        self.stop_time = False
        # Create a global variable to store the reference to the loop thread
        self.loop_thread_instance = None
        # Values to act upon
        self.selected_name = None
        self.selected_data = []
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Data Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''
    # Get the selected name (key) from the OptionMenu
    def get_data(self):
        self.selected_name = app.execute_name.get()
        if self.selected_name ==" ":
            app.display_message("Please select a name from the menu.")
            return False
        self.selected_data = app.data.get(self.selected_name, [])
        if self.selected_data == []:
            app.display_message(f"No data found for name: {self.selected_name}")
            return False
    # Sequence of Checks to perform actions based on data
    def loop_thread(self):
        self.get_data()
        for action in self.selected_data:
            if action[0] == "Hotkey":
                hotkey = action[1]
                break
        keyboard.on_press_key(hotkey, self.on_hotkey_event)
        keyboard.on_release_key(hotkey, self.on_hotkey_event)
        app.display_message(f"Press {hotkey} to start/stop the loop.")
        while self.programm_running:
            if self.loop_running:
                for key, value in self.selected_data:
                    if not self.loop_running:
                        break
                    elif key == "Sleep":
                        value = float(value)
                        time.sleep(value)
                    elif key == "Mouse Click":
                        mouse.click(value)
                    elif key == "Mouse Double Click":
                        mouse.double_click(value)
                    elif key == "Mouse Press":
                        mouse.press(value) 
                    elif key == "Mouse Release":
                        mouse.release(value) 
                    elif key == "Mouse Move":
                        x, y = map(int, value.split(','))
                        mouse.move(x, y,False)
                    elif key == "Absolute Mouse Move":
                        x, y = map(int, value.split(','))
                        mouse.move(x, y,True)
                    elif key == "Mouse Wheel":
                        delta = int(value)
                        mouse.wheel(delta)
                    elif key == "Keyboard Send":
                        keyboard.send(value)
                    elif key == "Keyboard Write":
                        keyboard.write(value)
                    elif key == "Keyboard Press":
                        keyboard.press(value)
                    elif key == "Keyboard Release":
                        keyboard.release(value)
                    elif key == "End":
                        app.display_message("End")
                        self.stop_time = time.time()
                        elapsed_time = self.stop_time - self.start_time
                        app.display_message(f"{elapsed_time:.1f} seconds passed")
                        self.loop_running = False
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Trigger Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''
    # Resets and switches on button press
    def on_hotkey_event(self,e):
        if e.event_type == keyboard.KEY_DOWN:
            if not self.falling_trigger:
                self.falling_trigger = True
                self.loop_running = not self.loop_running
                if self.loop_running:
                    app.display_message("Run")
                    self.start_time = time.time()
                else:
                    app.display_message("Pause")
                    self.stop_time = time.time()
                    elapsed_time = self.stop_time - self.start_time
                    app.display_message(f"{elapsed_time:.1f} seconds passed")
        elif e.event_type == keyboard.KEY_UP:
            self.falling_trigger = False
    # Start a looping daemon thread
    def start_programm(self):
        if self.loop_thread_instance and self.loop_thread_instance.is_alive():
            # loop thread is already running
            return
        if self.get_data() == False:
            return
        # Start Programm
        app.display_message(f"{self.selected_name} loaded and ready")
        self.programm_running = True
        # Deactivate the execution options
        app.execution_optionmenu.configure(state="disabled")
        # Looping Thread Call
        self.loop_thread_instance = threading.Thread(target=self.loop_thread)
        self.loop_thread_instance.daemon = True  # Set as daemon thread
        self.loop_thread_instance.start()
        # Update GUI
        app.stop_button.grid(row=0, column=0, padx=5)
        app.start_button.grid_forget()
        app.terminal_frame.update_idletasks
    # Stop a looping daemon thread
    def stop_programm(self):
        if not self.loop_thread_instance:
            # loop thread is not running
            return
        self.get_data()
        # Stop Programm
        app.display_message(f"{self.selected_name} quitting")
        self.programm_running = False
        # Stop the loop thread gracefully
        self.loop_running = False  
        # Reactivate the execution options
        app.execution_optionmenu.configure(state="normal")
        # Update GUI
        app.start_button.grid(row=0, column=0, padx=5)
        app.stop_button.grid_forget()
        app.terminal_frame.update_idletasks
'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tooltip GUI Class:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.get_tooltip_text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx()
        y += self.widget.winfo_rooty() + self.widget.winfo_height()

        self.tooltip = tk.Toplevel(self.widget,bg="light grey")
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip,bg="light grey")
        wrapped_text = textwrap.fill(text=self.get_tooltip_text(), width=25)
        label.config(text=wrapped_text)
        label.grid(padx=5,pady=5)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Main GUI Class:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
class Hotkey_Manager:   
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Base GUI Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''     
    def __init__(self):
        
        self.root = None

        # Define and initialize main variables
        self.action_add_run_times = 0
        self.display_message_run_times = 0
        self.action_type_comboboxes = []
        self.action_value_entries = []
        self.action_new_frame_list = []
        self.imported_data = []
        # Load data
        self.data = dict()
        self.data = self.load_exported_data()
        # Define GUI variables
        self.manager_frame = None
        self.control_frame = None
        self.terminal = None
        self.terminal_frame = None
        self.action_canvas = None
        self.action_frame = None
        self.action_frame_place = None
        self.scrollbar = None
        self.save_window = None
        self.load_window = None
        self.execution_frame = None
        self.start_button = None
        self.stop_button = None
        self.execute_name = None
        self.selected_name = None
        self.name_entry = None
        self.common_keys = [
                    "enter","space","esc","backspace","delete","insert","tab","capslock",
                    "numlock","pause","print","home","end","pageup","pagedown",
                    "up","down","left","right","ctrl","alt","shift",
                    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                    "#", "^", "*", "+", "-", "/", ",", ".", "<", "´",
                    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
                    ]
        self.action_types = {
                    "Hotkey":"Must be a key found on keyboard - examples:  f1, enter, u - numblock not supported",
                    "Sleep":"Must be any float number - Unit: seconds",                
                    "Mouse Click":"Must be: left, right or middle",
                    "Mouse Double Click":"Must be: left, right or middle",   
                    "Mouse Press":"Must be: left, right or middle",
                    "Mouse Release":"Must be: left, right or middle",       
                    "Absolute Mouse Move":"Must get 2 coordinates separated by comma - example: -246,619", 
                    "Mouse Move":"Must get 2 coordinates separated by comma - example: -246,619",           
                    "Mouse Wheel":"Must get any number, postitive is upwards, negative is downwards",
                    "Keyboard Send":"Must be a key found on keyboard - examples:  f1, enter, u - numblock not supported",
                    "Keyboard Press":"Must be a key found on keyboard - examples:  f1, enter, u - numblock not supported",       
                    "Keyboard Release":"Must be a key found on keyboard - examples:  f1, enter, u - numblock not supported",        
                    "Keyboard Write":"Anything goes",
                    "End":"Stops the loop at this point"
                    }
    def build(self):
        # Main Window
        self.root = tk.Tk()
        self.root.title("Hotkey Handler")
        self.root.resizable(False, False)
        self.root.columnconfigure(0, weight=1)
        # Left half of window
        self.manager_frame = tk.Frame(self.root)
        self.manager_frame.grid(row=2, column=0, sticky="n", pady=10, padx=(10, 0))
        self.manager_frame.grid_rowconfigure(0, weight=1)
        self.manager_frame.grid_columnconfigure(0, weight=1)
        # Separator between left and right
        separator = ttk.Separator(self.root, orient="vertical")
        separator.grid(row=2, column=3, sticky="ns", padx=10)
        # Right half of window 
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.grid(row=2, column=4, sticky="n", pady=10, padx=(0, 10))
        self.terminal_frame.grid_rowconfigure(0, weight=1)
        self.terminal_frame.grid_columnconfigure(0, weight=1)
        # Upper half of left frame
        self.control_frame = tk.Frame(self.manager_frame)
        self.control_frame.grid(row=0, column=0, padx=10, pady=(0, 10))
        # Create a new window for importing data in left frame
        self.load_window = tk.Frame(self.manager_frame)
        # Lower half of left frame
        self.action_canvas = tk.Canvas(self.manager_frame,highlightthickness=0,bg="grey")
        self.action_canvas.grid(row=2, column=0)
        # Create a new window for exporting data in left frame
        self.save_window = tk.Frame(self.manager_frame)
        # Upper Half of right frame
        self.execution_frame = tk.Frame(self.terminal_frame)
        self.execution_frame.grid(row=0, column=0)
        # Scrollbar for lower half of left frame
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.action_canvas.yview)
        self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"), yscrollcommand=self.scrollbar.set)
        self.action_canvas.bind("<Configure>", self.canvas_change)
        # Inner Holder for actions in lower half of left frame
        self.action_frame = tk.Frame(self.action_canvas)
        self.action_frame_place = self.action_canvas.create_window((0, 0), window=self.action_frame, anchor="n")
        # Buttons for data functionality in upper half of left frame
        add_action_button = ttk.Button(self.manager_frame, text="Add Action", command=self.add_action,style="Custom.TButton")
        add_action_button.grid(row=4, columnspan=3, column=0)
        save_button = ttk.Button(self.control_frame, text="Save Actions", command=self.save,style="Custom.TButton")
        save_button.grid(row=0, column=1)
        load_button = ttk.Button(self.control_frame, text="Load Actions", command=self.load,style="Custom.TButton")
        load_button.grid(row=0, column=0)
        # Terminal space to display feedback in lower half of right frame
        terminal_label = ttk.Label(self.terminal_frame,text="Terminal:")
        terminal_label.grid(row=1, column=0, sticky="w")
        self.terminal = scrolledtext.ScrolledText(self.terminal_frame, wrap=tk.WORD, state=tk.DISABLED, width=75, height=10)
        self.terminal.configure(font=("Arial", 9))#Helvetica
        self.terminal.grid(row=2, column=0, sticky="n")
        # Buttons for hotkey functionality in upper Half of right frame
        self.start_button = ttk.Button(self.execution_frame, text="Start",command=Hotkey_main_instance.start_programm,style="Custom.TButton")
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(self.execution_frame, text="Stop",command=Hotkey_main_instance.stop_programm,style="Custom.TButton")
        # Add the name/key of Import Optionmenu
        self.import_name_var = tk.StringVar()
        # Add the name/key of Execution Optionmenu
        self.execute_name = tk.StringVar()
        self.execution_optionmenu_border = tk.Frame(self.execution_frame, borderwidth=1,relief="groove")
        self.execution_optionmenu_border.grid(row=1, column=0, pady=10)
        self.execution_optionmenu = ttk.OptionMenu(self.execution_optionmenu_border, self.execute_name," ")
        self.execution_option_reload()
        # Create a Sytle
        self.style = ttk.Style()
        # Define a custom style for the normal state
        self.style.configure("Custom.TButton", relief="solid")
        # Initialize Hotkey
        self.add_action("Hotkey")
    def run(self):
        self.root.mainloop()
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Support GUI Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    

    '''
    # Methods for the Execution Optionmenu in reference to hotkey class
    def execution_option_reload(self):
        # Reload Data
        self.data.update(self.load_exported_data())
        # Reload Menu
        self.execution_optionmenu.destroy()
        execution_options = list(self.data.keys()) if self.data else [" "]
        self.execution_optionmenu = ttk.OptionMenu(self.execution_optionmenu_border, self.execute_name," ", *execution_options)
        self.execution_optionmenu.grid()
        self.execution_optionmenu.config(width=25)
    # Method to display a message in the terminal
    def display_message(self,message):
        def inner_separator(widget,separator_object,middle_object):
            # Get the font size used in the text widget
            font_size_pixel = tkfont.Font(font=widget.cget("font")).measure(separator_object)
            middle_object_pixel = tkfont.Font(font=widget.cget("font")).measure(middle_object)
            line_length_pixel = widget.winfo_width()-2
            # Calculate the length of the separator line before and after the middle object
            separator_length_after = line_length_pixel//font_size_pixel//2
            separator_length_before = (line_length_pixel - middle_object_pixel*2)//font_size_pixel//2
            # Create the separator line
            separator = separator_object * separator_length_before + str(middle_object) + separator_object * separator_length_after
            return separator

        self.terminal.config(state=tk.NORMAL)  # Set the state to normal to allow editing
        self.terminal.insert(tk.END, inner_separator(self.terminal,"-",self.display_message_run_times))
        self.terminal.insert(tk.END, "\n")
        self.terminal.insert(tk.END, message)  # Insert the message
        self.terminal.insert(tk.END, "\n")
        self.terminal.config(state=tk.DISABLED)  # Set the state back to disabled
        self.terminal.see(tk.END)
        self.display_message_run_times += 1
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Canvas GUI Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''
    # Method to update the canvas and action frame position
    def canvas_change(self,event=None):
        # Reload Widgets within Canvas
        self.action_canvas.update_idletasks()
        # Define the width of the canvas
        self.action_canvas.config(width=self.action_frame.winfo_reqwidth())
        # Calculate the x-position to center the action_frame
        x_position = (self.action_canvas.winfo_width() - self.action_frame.winfo_reqwidth()) / 2 + self.action_frame.winfo_reqwidth() / 2
        # Set the position of the action_frame within the canvas
        self.action_canvas.coords(self.action_frame_place, x_position, 0)
        # Calculate the total height required for all child widgets in the action_frame
        total_child_height = sum(child.winfo_reqheight() for child in self.action_frame.winfo_children())
        # Set a maximum canvas height to avoid excessive scrolling
        self.action_canvas.config(height=min(150, total_child_height))
        # Show the scrollbar and adjust the canvas scroll region
        self.scrollbar.grid(row=2, column=1, sticky="ns",padx=(10,0))
        self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"))
    # Method to add an action
    def add_action(self,action_type="Sleep", action_value=""):
        self.action_canvas.event_generate("<Configure>")
        if self.action_add_run_times == 0:
            action_type = "Hotkey"
        if action_type == "Hotkey":
            self.action_add_run_times = 0
        if self.action_add_run_times >= 999:
            self.display_message("reached the maximum number of actions")
            return
        self.action_add_run_times += 1

        new_action_frame = tk.Frame(self.action_frame)
        new_action_frame.grid(row=len(self.action_type_comboboxes) + 1, column=0,padx=10)
        self.action_new_frame_list.append(new_action_frame)
        new_action_label = ttk.Label(new_action_frame, text=f"{self.action_add_run_times:03}",padding=(1,2))
        new_action_label.grid(row=0, column=0)

        new_action_type_combobox = tk.StringVar()
        action_type_optionmenu_border = tk.Frame(new_action_frame, borderwidth=1,relief="groove")
        action_type_optionmenu_border.grid(row=0, column=1)
        if action_type == "Hotkey":
            new_action_type_option_menu = ttk.OptionMenu(action_type_optionmenu_border, new_action_type_combobox, "Hotkey")
        else:
            new_action_type_option_menu = ttk.OptionMenu(action_type_optionmenu_border, new_action_type_combobox,action_type,*list(item for item in self.action_types.keys() if item != "Hotkey"))
        new_action_type_option_menu.config(width=20)
        new_action_type_option_menu.grid(row=0, column=0)
        
        def get_tooltip_text():
            return self.action_types.get(new_action_type_combobox.get(), "")

        Tooltip(new_action_type_option_menu, get_tooltip_text)

        new_action_value_entry = ttk.Entry(new_action_frame, width=25,takefocus=False)
        new_action_value_entry.grid(row=0, column=2, pady=(1,3))
        new_action_value_entry.insert(0, action_value)  # Default Value
        if action_type == "End":
            new_action_value_entry.configure(state="readonly")

        new_delete_action_button = ttk.Button(self.manager_frame, text="X",style="Custom.TButton", command=self.delete_action)
        new_delete_action_button.grid(row=3, columnspan=3, column=0)

        new_action_frame.grid_columnconfigure(0, weight=1)
        new_action_frame.grid_columnconfigure(1, weight=1)

        self.action_type_comboboxes.append(new_action_type_combobox)
        self.action_value_entries.append(new_action_value_entry)
        
        self.action_canvas.event_generate("<Configure>")
        self.action_canvas.yview_moveto(1.0)
    def delete_action(self):
        self.action_canvas.event_generate("<Configure>")
        # Check if there are actions to delete
        if self.action_add_run_times > 1:
            # Remove the last new action frame from the GUI
            self.action_new_frame_list[-1].destroy()
            # Decrement the run time index
            self.action_add_run_times -= 1
            # Remove the corresponding entries from the lists
            del self.action_type_comboboxes[-1]
            del self.action_value_entries[-1]
            del self.action_new_frame_list[-1]
        else:
            self.display_message("cannot delete Hotkey")
        self.action_canvas.event_generate("<Configure>")
        self.action_canvas.yview_moveto(1.0)
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Action Set GUI Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''
    # Methods for loading and deleting data
    def load(self):
        # Clear Space to prevent stacking
        self.load_window.destroy()
        # Reload data
        self.data.update(self.load_exported_data())
        # Create a new window for importing data
        self.load_window = tk.Frame(self.manager_frame)
        self.load_window.grid(row=1, padx=10, pady=(0, 10))
        import_options = list(self.data.keys()) if self.data else [""]
        load_optionmenu_border = tk.Frame(self.load_window, borderwidth=1,relief="groove")
        load_option_menu = ttk.OptionMenu(load_optionmenu_border, self.import_name_var,"", *import_options)
        load_option_menu.grid()
        load_option_menu.config(width=25)
        # Add a "Load" button
        load_button = ttk.Button(self.load_window, text="Load", command=self.load_action_set,style="Custom.TButton")
        # Add a "Delete" button
        delete_button = ttk.Button(self.load_window, text="Delete", command=self.delete_action_set,style="Custom.TButton")
        # Give No Data Feedback
        load_empty_list_fault = ttk.Label(self.load_window, text="No Data")
        # Add a "Close" button
        close_button = ttk.Button(self.load_window, text="Close", command=self.load_window.destroy,style="Custom.TButton")
        close_button.grid(row=3, columnspan=2)
        if import_options != [""]:
            load_optionmenu_border.grid(row=1, columnspan=2)
            load_button.grid(row=2, column=1, sticky="w")
            delete_button.grid(row=2, column=0, sticky="e")
        else:
            load_empty_list_fault.grid(row=0, columnspan=2)
        
    def load_action_set(self):
        self.selected_name = self.import_name_var.get()
        self.imported_data = self.data.get(self.selected_name, [])
        # Check data for content
        if self.imported_data:
            # Clear the existing GUI actions
            for frame in self.action_frame.winfo_children():
                frame.destroy()
            self.action_type_comboboxes.clear()
            self.action_value_entries.clear()
            # Check if the first action is "Hotkey"
            if self.imported_data[0][0] != "Hotkey":
                # If not, add an empty "Hotkey" action at index 0
                self.imported_data.insert(0, ["Hotkey", ""])
            # Create new action frames based on imported data
            for action_type, action_value in self.imported_data:
                self.add_action(action_type, action_value)
        else:
            self.display_message(f"No data found for name: {self.selected_name}")
        # Close the Load window
        self.load_window.destroy()
    def delete_action_set(self):
        self.selected_name = self.import_name_var.get()
        if self.selected_name in self.data:
            del self.data[self.selected_name]
            self.save_exported_data()
            self.display_message(f"Deleted action set '{self.selected_name}'")
            # Clear the name selection
            self.import_name_var.set("")
            # Reload Data
            self.load()
            # Give Feedback
            Data_deleted = ttk.Label(self.load_window, text=f"{self.selected_name} deleted")
            Data_deleted.grid(row=0, columnspan=2)
        else:
            self.display_message(f"No action set found for name: {self.selected_name}")
    # Methods for saving current Data
    def save(self):
        # Clear Space to prevent stacking
        self.save_window.destroy()
        # Reload data
        self.data.update(self.load_exported_data())
        # Create a new window for exporting data
        self.save_window = tk.Frame(self.manager_frame)
        self.save_window.grid(row=5, padx=10, pady=10)
        # Add a Label and an Entry widget to input the name
        name_label = ttk.Label(self.save_window, text="Enter a name for this action set:")
        name_label.grid()
        self.name_entry = ttk.Entry(self.save_window)
        self.name_entry.grid(pady=(0, 5))
        if self.imported_data:
            self.name_entry.insert(0, self.selected_name)
        # Add an "Enter" button to confirm the name
        enter_button = ttk.Button(self.save_window, text="Enter", command=self.save_action_set,style="Custom.TButton")
        enter_button.grid()
    def save_action_set(self):
        self.current_actions_nested_list = []
        for each in range(len(self.action_type_comboboxes)):
            action_type = self.action_type_comboboxes[each].get()
            action_value = self.action_value_entries[each].get()
            self.current_actions_nested_list.append((action_type, action_value))
        name = self.name_entry.get()
        if name:
            if not self.check_data_for_export() == False:
                self.data[name] = self.current_actions_nested_list
                self.display_message(f"{name}={self.current_actions_nested_list}")
                self.save_exported_data()
            self.save_window.destroy()
        else:
                self.display_message("Please enter a name.")
    '''


    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Data Verification Methods:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    '''
    # Method to verify the value inputs
    def check_data_for_export(self):
        fault_list = []
        i = 0
        for key, value in self.current_actions_nested_list:
            i += 1
            if key == "Sleep": 
                if re.match(r'^\s*-?\d+(\.\d+)?\s*$',value):
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: number - unit: seconds")
                    fault_list.append(key)
            elif key == "Mouse Click":
                if value in ["right","left","middle"]:
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be either: right, left, middle")
                    fault_list.append(key)
            elif key == "Mouse Double Click":
                if value in ["right","left","middle"]:
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be either: right, left, middle")
                    fault_list.append(key)
            elif key == "Mouse Press":
                if value in ["right","left","middle"]:
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be either: right, left, middle")
                    fault_list.append(key)
            elif key == "Mouse Release":
                if value in ["right","left","middle"]:
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be either: right, left, middle")
                    fault_list.append(key)
            elif key == "Mouse Move":
                if re.match(r'^\s*-?\d+,-?\d+\s*$', value):
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: int number - form: number_1, number_2")
                    fault_list.append(key)
            elif key == "Absolute Mouse Move":
                if re.match(r'^\s*-?\d+,-?\d+\s*$', value):
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: int number - form: number_1, number_2")
                    fault_list.append(key)
            elif key == "Mouse Wheel":
                if re.match(r'^\s*-?\d+\s*$',value):
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: int number")
                    fault_list.append(key)
            elif key == "Keyboard Send":
                if value in self.common_keys:
                    continue
                elif "+" in value:
                    for each in value.split("+"):
                        if each in self.common_keys:
                            continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: common key alone or combined with +")
                    fault_list.append(key)
            elif key == "Keyboard Press":
                if value in self.common_keys:
                    continue
                elif "+" in value:
                    for each in value.split("+"):
                        if each in self.common_keys:
                            continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: common key alone or combined with +")
                    fault_list.append(key)
            elif key == "Keyboard Release":
                if value in self.common_keys:
                    continue
                elif "+" in value:
                    for each in value.split("+"):
                        if each in self.common_keys:
                            continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: common key alone or combined with +")
                    fault_list.append(key)
            elif key == "Hotkey":
                if value in self.common_keys:
                    continue
                else:
                    self.display_message(f"Fault at key: {i:03} - {key} - with value: {value} - should be type: common key")
                    fault_list.append(key)        
            # Skipping check for Keyboard Write since any string is ok
        # Evaluation to request saving if no fault
        if fault_list == []:
            return True
        else:
            self.display_message(f"{len(fault_list)} errors have been found" if len(fault_list)>1 else "1 error has been found")
            return False

    # Method to save exported data to a JSON file
    def save_exported_data(self):
        with open("exported_data.json", "w") as json_file:
            json.dump(self.data, json_file)
        self.execution_option_reload()
    # Method to load exported data from a JSON file
    def load_exported_data(self):
        try:
            with open("exported_data.json", "r") as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError:
            print("File 'exported_data.json' not found.")  # Print an error message for debugging
            return {}
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)  # Print JSON decoding error for debugging
            return {}


if __name__ == "__main__":
    Hotkey_main_instance = Hotkey_Loop()
    app = Hotkey_Manager()
    app.build()
    app.run()






        