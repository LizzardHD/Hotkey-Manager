
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import json
import threading
import atexit
import keyboard
import mouse
import time



# Dictionary to store exported data
exported_data = {}
# Create the main Tkinter window and Class Instances
root = tk.Tk()


'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Hotkey Class:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
class Hotkey:
    def __init__(self):
        # Variables for starting and stopping the Hotkey
        self.programm_running = False
        self.loop_running = False
        self.falling_trigger = False
        # Create a global variable to store the reference to the loop thread
        self.loop_thread_instance = None
        # Values to act upon
        self.selected_name = None
        self.selected_data = []
    def get_data(self):
        # Get the selected name (key) from the OptionMenu
        self.selected_name = app.get_name_key()
        if not self.selected_name:
            app.display_message("Please select a name from the list.")
            return
        self.selected_data = exported_data.get(self.selected_name, [])
        if self.selected_data == []:
            app.display_message(f"No data found for name: {self.selected_name}")
            return
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
                print("loop")
                for key, value in self.selected_data:
                    if not self.loop_running:
                        break
                    elif key == "Sleep":
                        try:
                            value = float(value)
                            time.sleep(value)
                        except Exception as e:
                            print(f"{e} Fault at key {key} with value: {value}")
                            continue
                    elif key == "Mouse Click":
                        mouse.click(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Double Click":
                        mouse.double_click(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Press":
                        mouse.press(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Release":
                        mouse.release(value)  # 'value' should be 'left', 'right', or 'middle'
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
    def on_hotkey_event(self,e):
        if e.event_type == keyboard.KEY_DOWN:
            if not self.falling_trigger:
                self.falling_trigger = True
                self.loop_running = not self.loop_running
                if self.loop_running:
                    app.display_message("Run")
                else:
                    app.display_message("Pause")
        elif e.event_type == keyboard.KEY_UP:
            self.falling_trigger = False
    def start_programm(self):
        if self.loop_thread_instance and self.loop_thread_instance.is_alive():
            # loop thread is already running
            return
        self.get_data()
        # Start Programm
        app.display_message(f"{self.selected_name} loaded and ready")
        self.programm_running = True
        self.loop_thread_instance = threading.Thread(target=self.loop_thread)
        self.loop_thread_instance.daemon = True  # Set as daemon thread
        self.loop_thread_instance.start()
        # Update GUI
        app.stop_button.grid(row=0, column=0, padx=5)
        app.start_button.grid_forget()
        app.terminal_frame.update_idletasks
    def stop_programm(self):
        if not self.loop_thread_instance:
            # loop thread is not running
            return
        self.get_data()
        # Stop Programm
        app.display_message(f"{self.selected_name} quitting")
        self.programm_running = False
        self.loop_running = False  # Stop the loop thread gracefully
        # Update GUI
        app.start_button.grid(row=0, column=0, padx=5)
        app.stop_button.grid_forget()
        app.terminal_frame.update_idletasks
    def at_exit(self):
        self.programm_running = False
        self.loop_running = False
Hotkey_main_instance = Hotkey()
'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Main GUI Class:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
class Hotkey_Manager:        
    def __init__(self,window):
        self.root = window
        if not isinstance(self.root,tk.Tk):
            print(f"Error in Datatype of {root} should be instance tk.Tk")
            return
        self.root.title("Hotkey Handler")
        self.root.resizable(False, False)
        self.root.columnconfigure(0, weight=1)
        self.Load_exported_data()
        # Define and initialize main variables
        self.action_add_run_times = 0
        self.display_message_run_times = 0
        self.action_type_comboboxes = []
        self.action_value_entries = []
        self.action_new_frame_list = []
        self.data = exported_data
        self.imported_data = []
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
        self.action_canvas.grid(row=3, column=0)
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
        add_action_button.grid(row=4, columnspan=10, sticky="s")
        save_button = ttk.Button(self.control_frame, text="Save Actions", command=self.save,style="Custom.TButton")
        save_button.grid(row=0, column=1)
        Load_button = ttk.Button(self.control_frame, text="Load Actions", command=self.load,style="Custom.TButton")
        Load_button.grid(row=0, column=0)
        # Terminal space to display feedback in lower half of right frame
        terminal_label = ttk.Label(self.terminal_frame,text="Terminal:")
        terminal_label.grid(row=1, column=0, sticky="w")
        self.terminal = scrolledtext.ScrolledText(self.terminal_frame, wrap=tk.WORD, state=tk.DISABLED, width=75, height=10)
        self.terminal.configure(font=("Helvetica", 9))
        self.terminal.grid(row=2, column=0, sticky="n")
        # Buttons for hotkey functionality in upper Half of right frame
        self.start_button = ttk.Button(self.execution_frame, text="Start",command=Hotkey_main_instance.start_programm,style="Custom.TButton")
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(self.execution_frame, text="Stop",command=Hotkey_main_instance.stop_programm,style="Custom.TButton")
        # Add the name/key of Import Optionmenu
        self.import_name_var = tk.StringVar()
        self.import_name_var.set("") # Default selection
        self.selected_name = None
        # Add the name/key of Execution Optionmenu
        self.name_key = tk.StringVar()
        self.name_key.set(" ") # Default Selection
        execution_options = list(self.data.keys()) if self.data else [""]
        execution_optionmenu_border = tk.Frame(self.execution_frame, borderwidth=1,relief="groove")
        execution_optionmenu_border.grid(row=1, column=0, pady=10)
        self.name_option = ttk.OptionMenu(execution_optionmenu_border, self.name_key, *execution_options, command=self.update_name_option)
        self.name_option.grid()
        self.name_option.config(width=25)
        self.update_name_option()  # Initialize the OptionMenu
        # Create a Sytle
        self.style = ttk.Style()
        # Define a custom style for the normal state
        self.style.configure("Custom.TButton", relief="solid")
        # Initialize Hotkey
        self.add_action("Hotkey")
    
    # Functions for the Execution Optionmenu
    def update_name_option(self):
        # Clear the existing options
        self.name_option['menu'].delete(0, 'end')
        # Update the list of action set names
        action_set_names = list(self.data.keys())
        for name in action_set_names:
            self.name_option['menu'].add_command(label=name, command=lambda name=name: self.name_key.set(name))
    def get_name_key(self):
        return self.name_key.get()
    # Function to display a message in the terminal
    def display_message(self,message):
        if self.display_message_run_times > 999:
            self.display_message_run_times = 0
        self.terminal.config(state=tk.NORMAL)  # Set the state to normal to allow editing
        self.terminal.insert(tk.END, f"---------------------------------------------------------------{self.display_message_run_times:03}---------------------------------------------------------------")
        self.terminal.insert(tk.END, "\n")
        self.terminal.insert(tk.END, message)  # Insert the message
        self.terminal.insert(tk.END, "\n")
        self.terminal.config(state=tk.DISABLED)  # Set the state back to disabled
        self.terminal.see(tk.END)
        self.display_message_run_times += 1
    # Function to save exported data to a JSON file
    def save_exported_data(self):
        exported_data = self.data 
        with open("exported_data.json", "w") as json_file:
            json.dump(exported_data, json_file)
        self.update_name_option()
    # Function to load exported data from a JSON file
    def Load_exported_data(self):
        try:
            with open("exported_data.json", "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}
    # Function to update the canvas and action frame position
    def canvas_change(self,event=None):
        # Define the width of the canvas
        self.action_canvas.config(width=self.action_frame.winfo_reqwidth())
        # Calculate the x-position to center the action_frame
        x_position = (self.action_canvas.winfo_width() - self.action_frame.winfo_reqwidth()) / 2 + self.action_frame.winfo_reqwidth() / 2
        # Set the position of the action_frame within the canvas
        self.action_canvas.coords(self.action_frame_place, x_position, 0)
        # Calculate the total height required for all child widgets in the action_frame
        total_child_height = sum(child.winfo_reqheight() for child in self.action_frame.winfo_children())
        # Configure the action_canvas scroll region to fit all widgets
        self.action_canvas.configure(scrollregion=(0,0,0,total_child_height))
        # Set a maximum canvas height to avoid excessive scrolling
        self.action_canvas.config(height=min(150, total_child_height))
        # Show the scrollbar and adjust the canvas scroll region
        self.scrollbar.grid(row=2, column=1, sticky="ns",padx=(10,0))
        self.action_canvas.config(scrollregion=(0,0,0,total_child_height))
        '''
        # Check if the action_frame height exceeds the canvas height
        if self.action_frame.winfo_reqheight() > self.action_canvas.winfo_height():
        else:
            # Hide the scrollbar and adjust the canvas scroll region
            self.scrollbar.grid_remove()
            self.action_canvas.config(scrollregion=(0,0,0,total_child_height))
        '''
        print(self.action_add_run_times," - runtime")
        print(self.action_canvas.winfo_height()," - canvas")
        print(self.action_frame.winfo_reqheight()," - frame")
        print(total_child_height," - childs")
        self.update_name_option()
        
    # Function to add an action
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
        new_action_type_combobox.set(action_type)  # Default Selection
        action_type_optionmenu_border = tk.Frame(new_action_frame, borderwidth=1,relief="groove")
        action_type_optionmenu_border.grid(row=0, column=1)
        if action_type == "Hotkey":
            new_action_type_option_menu = ttk.OptionMenu(action_type_optionmenu_border, new_action_type_combobox, "Hotkey")
        else:
            new_action_type_option_menu = ttk.OptionMenu(action_type_optionmenu_border, new_action_type_combobox,
                                                        "Sleep",                "Mouse Click",
                                                        "Mouse Double Click",   "Mouse Press",
                                                        "Mouse Release",        "Absolute Mouse Move", 
                                                        "Mouse Move",           "Mouse Wheel",
                                                        "Keyboard Send",        "Keyboard Write",
                                                        "Keyboard Press",       "Keyboard Release")
        new_action_type_option_menu.config(width=20)
        new_action_type_option_menu.grid(row=0, column=0)

        new_action_value_entry = ttk.Entry(new_action_frame, width=25,takefocus=False)
        new_action_value_entry.grid(row=0, column=2, pady=(1,3))
        new_action_value_entry.insert(0, action_value)  # Default Value

        new_delete_action_button = ttk.Button(self.manager_frame, text="X",style="Custom.TButton", command=self.delete_action)
        new_delete_action_button.grid(row=5, columnspan=10, sticky="s")

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
    # Functions for loading and deleting data
    def load(self):
        # Clear Space to prevent stacking
        self.load_window.destroy()
        # Reload data
        self.data.update(self.Load_exported_data())
        # Create a new window for importing data
        self.load_window = tk.Frame(self.manager_frame)
        self.load_window.grid(row=2, padx=10, pady=(0, 10))
        import_options = list(self.data.keys()) if self.data else [""]
        Load_option_menu = ttk.OptionMenu(self.load_window, self.import_name_var, *import_options)
        Load_option_menu.config(width=25)
        # Add a "Load" button
        Load_button = ttk.Button(self.load_window, text="Load", command=self.load_action_set,style="Custom.TButton")
        # Add a "Delete" button
        delete_button = ttk.Button(self.load_window, text="Delete", command=self.delete_action_set,style="Custom.TButton")
        # Give No Data Feedback
        Load_empty_list_fault = ttk.Label(self.load_window, text="No Data")
        # Add a "Close" button
        close_button = ttk.Button(self.load_window, text="Close", command=self.load_window.destroy,style="Custom.TButton")
        close_button.grid(row=3, columnspan=2)
        if import_options != []:
            Load_option_menu.grid(row=1, columnspan=2)
            Load_button.grid(row=2, column=1, sticky="w")
            delete_button.grid(row=2, column=0, sticky="e")
        else:
            Load_empty_list_fault.grid(row=0, columnspan=2)
        self.update_name_option()
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
            # Close and reopen the window
            self.load_window.destroy()
            self.load()
            # Give Feedback
            Data_deleted = ttk.Label(self.load_window, text=f"{self.selected_name} deleted")
            Data_deleted.grid(row=0, columnspan=2)
        else:
            self.display_message(f"No action set found for name: {self.selected_name}")
    # Functions for saving current Data
    def save(self):
        # Clear Space to prevent stacking
        self.save_window.destroy()
        # Reload data
        self.data.update(self.Load_exported_data())
        self.current_data = []
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
        self.data.update(self.Load_exported_data())
        
        for each in range(len(self.action_type_comboboxes)):
            action_type = self.action_type_comboboxes[each].get()
            action_value = self.action_value_entries[each].get()
            self.current_data.append((action_type, action_value))
        name = self.name_entry.get()
        if name:
            self.data[name] = self.current_data
            self.save_exported_data()
            self.display_message(f"{name}={self.current_data}")
            self.save_window.destroy()
        else:
            self.display_message("Please enter a name.")



app = Hotkey_Manager(root)



# Ensure smooth exit
atexit.register(Hotkey_main_instance.at_exit)
# Load exported data
exported_data.update(app.Load_exported_data())

root.mainloop()



        