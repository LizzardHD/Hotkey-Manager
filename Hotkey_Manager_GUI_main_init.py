
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
        self.selected_name = Optionmenu_Hotkey_Choice_Instance.get_selected_name()
        if not self.selected_name:
            display_message("Please select a name from the list.")
            return
        self.selected_data = exported_data.get(self.selected_name, [])
        if self.selected_data == []:
            display_message(f"No data found for name: {self.selected_name}")
            return
    def loop_thread(self):
        self.get_data()
        for action in self.selected_data:
            if action[0] == "Hotkey":
                hotkey = action[1]
                break
        keyboard.on_press_key(hotkey, self.on_hotkey_event)
        keyboard.on_release_key(hotkey, self.on_hotkey_event)
        display_message(f"Press {hotkey} to start/stop the loop.")
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
                    display_message("Run")
                else:
                    display_message("Pause")
        elif e.event_type == keyboard.KEY_UP:
            self.falling_trigger = False
    def start_programm(self):
        if self.loop_thread_instance and self.loop_thread_instance.is_alive():
            # loop thread is already running
            return
        self.get_data()
        # Start Programm
        display_message(f"{self.selected_name} loaded and ready")
        self.programm_running = True
        self.loop_thread_instance = threading.Thread(target=self.loop_thread)
        self.loop_thread_instance.daemon = True  # Set as daemon thread
        self.loop_thread_instance.start()
        # Update GUI
        stop_button.grid(row=0, column=0, padx=5)
        start_button.grid_forget()
        terminal_frame.update_idletasks
    def stop_programm(self):
        if not self.loop_thread_instance:
            # loop thread is not running
            return
        self.get_data()
        # Stop Programm
        display_message(f"{self.selected_name} quitting")
        self.programm_running = False
        self.loop_running = False  # Stop the loop thread gracefully
        # Update GUI
        start_button.grid(row=0, column=0, padx=5)
        stop_button.grid_forget()
        terminal_frame.update_idletasks
    def at_exit(self):
        self.programm_running = False
        self.loop_running = False
        
Hotkey_main_instance = Hotkey()

'''


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Main GUI Classes:
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


'''
# Class and function to create and update the hotkey option menu
class Optionmenu_Hotkey_Choice:
    def __init__(self, master, exported_data):
        self.master = master
        self.name_key = tk.StringVar()
        self.name_key.set(" ")
        self.name_option = tk.OptionMenu(master, self.name_key, *list(exported_data.keys()), command=self.update_name_option)
        self.name_option.grid(row=1, column=0, pady=10)
        self.name_option.config(width=25)
        self.update_name_option()  # Initialize the OptionMenu
    def update_name_option(self):
        # Clear the existing options
        self.name_option['menu'].delete(0, 'end')
        # Update the list of action set names
        action_set_names = list(exported_data.keys())
        for name in action_set_names:
            self.name_option['menu'].add_command(label=name, command=lambda name=name: self.name_key.set(name))
    def get_selected_name(self):
        return self.name_key.get()
    @classmethod
    def create_instance(cls, master, exported_data):
        return cls(master, exported_data)
# Class to save the current actions
class save_action_set:
    def __init__(self):
        self.current_data = []
    def save_creator(self):
        # Create a new window for exporting data
        self.save_window = tk.Frame(app.create_widgets.manager_frame)
        self.save_window.grid(row=5, padx=10, pady=10)
        # Add a Label and an Entry widget to input the name
        self.name_label = tk.Label(self.save_window, text="Enter a name for this action set:")
        self.name_label.grid()
        self.name_entry = tk.Entry(self.save_window)
        self.name_entry.insert(0, self.Load_actions)
        self.name_entry.grid(pady=(0, 5))
        # Add an "Enter" button to confirm the name
        self.enter_button = tk.Button(self.save_window, text="Enter", command=self.save_with_name)
        self.enter_button.grid()

    def save_with_name(self):
        app.data.update(app.Load_exported_data())
        
        for each in range(len(app.action_type_comboboxes)):
            action_type = app.action_type_comboboxes[each].get()
            action_value = app.action_value_entries[each].get()
            self.current_data.append((action_type, action_value))
        name = self.name_entry.get()
        if name:
            app.data[name] = self.current_data
            app.save_exported_data()
            app.display_message(f"{name}={list(self.data[name])}")
            self.save_window.destroy()
        else:
            app.display_message("Please enter a name.")
    def Load_actions(self):
        def import_data():
            self.selected_name = import_name_var.get()
            self.imported_data = self.data.get(self.selected_name, [])

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
                display_message(f"No data found for name: {self.selected_name}")

            # Close the Load window
            self.Load_window.destroy()

        def delete_action_set():
            self.selected_name = import_name_var.get()
            if self.selected_name in self.data:
                del self.data[self.selected_name]
                self.save_exported_data()
                self.display_message(f"Deleted action set '{self.selected_name}'")
                # Clear the name selection
                import_name_var.set("")
                # Give Feedback
                Data_deleted = tk.Label(Load_window, text=f"{self.selected_name} deleted")
                Data_deleted.grid(row=0, columnspan=2)
                # Clear the existing options
                Load_option_menu['menu'].delete(0, 'end')
                # Update the list of import names and recreate the OptionMenu
                import_names = list(self.data.keys())
                for name in import_names:
                    Load_option_menu['menu'].add_command(label=name, command=tk._setit(import_name_var, name))
            else:
                self.display_message(f"No action set found for name: {self.selected_name}")

        # Reload data
        self.data.update(self.Load_exported_data())

        # Create a new window for importing data
        self.Load_window = tk.Frame(self.manager_frame)
        self.Load_window.grid(row=2, padx=10, pady=(0, 10))

        # Add an OptionMenu to select the name/key
        import_name_var = tk.StringVar()
        import_name_var.set("")  # Default selection
        import_names = list(self.data.keys())
        try:
            Load_option_menu = tk.OptionMenu(self.Load_window, import_name_var, *import_names)
            Load_option_menu.grid(row=1, columnspan=2)
            Load_option_menu.config(width=25)
            # Add a "Load" button
            Load_button = tk.Button(self.Load_window, text="Load", command=import_data)
            Load_button.grid(row=2, column=1, sticky="w")
            # Add a "Delete" button
            delete_button = tk.Button(self.Load_window, text="Delete", command=delete_action_set)
            delete_button.grid(row=2, column=0, sticky="e")
        except:
            # Give Feedback
            Load_empty_list_fault = tk.Label(self.Load_window, text="No Data")
            Load_empty_list_fault.grid(row=0, columnspan=2)
        finally:
            # Add a "Close" button
            close_button = tk.Button(self.Load_window, text="Close", command=self.Load_window.destroy)
            close_button.grid(row=3, columnspan=2)
        Optionmenu_Hotkey_Choice_Instance.update_name_option()

class Hotkey_Manager:        
    def __init__(self,root,data=exported_data):
        self.root = root
        self.root.title("Hotkey Handler")
        self.root.resizable(False, False)
        self.root.columnconfigure(0, weight=1)
        # Define and initialize GUI components
        self.action_add_run_times = 0
        self.display_message_run_times = 0
        self.action_type_comboboxes = []
        self.action_value_entries = []
        self.action_single_frame = []
        self.data = data
    # Function to display a message in the terminal
    def display_message(self,message):
        global display_message_run_times
        if display_message_run_times > 999:
            display_message_run_times = 0
        terminal.config(state=tk.NORMAL)  # Set the state to normal to allow editing
        terminal.insert(tk.END, f"------------------------------------{display_message_run_times:03}------------------------------------")
        terminal.insert(tk.END, "\n")
        terminal.insert(tk.END, message)  # Insert the message
        terminal.insert(tk.END, "\n")
        terminal.config(state=tk.DISABLED)  # Set the state back to disabled
        terminal.see(tk.END)
        display_message_run_times += 1
    # Function to save exported data to a JSON file
    def save_exported_data(self):
        exported_data = self.data 
        with open("exported_data.json", "w") as json_file:
            json.dump(exported_data, json_file)
        Optionmenu_Hotkey_Choice_Instance.update_name_option()
    # Function to load exported data from a JSON file
    def Load_exported_data(self):
        try:
            with open("exported_data.json", "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}
    # Function to update the canvas and action frame position
    def on_configure(self,event=None):
        # Configure the action_canvas scroll region to fit all widgets
        action_canvas.configure(scrollregion=action_canvas.bbox("all"))
        # Check if the canvas width is greater than the action_frame's requested width
        if action_canvas.winfo_width() > action_frame.winfo_reqwidth():
            # Calculate the x-position to center the action_frame
            x_position = (action_canvas.winfo_width() - action_frame.winfo_reqwidth()) / 2 + action_frame.winfo_reqwidth() / 2
            # Set the position of the action_frame within the canvas
            action_canvas.coords(action_frame_place, x_position, 0)
        else:
            # Center the action_frame in the canvas when canvas is smaller
            x_position = action_canvas.winfo_width() / 2
            action_canvas.coords(action_frame_place, x_position, 0)
        # Calculate the total height required for all child widgets in the action_frame
        total_child_height = sum(child.winfo_reqheight() for child in action_frame.winfo_children())
        # Set a maximum canvas height to avoid excessive scrolling
        action_canvas.config(height=min(300, total_child_height))
        # Check if the action_frame height exceeds the canvas height
        if action_frame.winfo_reqheight() > action_canvas.winfo_height():
            # Show the scrollbar and adjust the canvas scroll region
            scrollbar.grid(row=2, column=1, sticky="ns")
            action_canvas.config(scrollregion=action_canvas.bbox("all"))
        else:
            # Hide the scrollbar and adjust the canvas scroll region
            scrollbar.grid_remove()
            action_canvas.config(scrollregion=action_canvas.bbox("all"))
        # Update the Optionmenu_Hotkey_Choice_Instance to refresh the displayed names
        Optionmenu_Hotkey_Choice_Instance.update_name_option()
        # Update the canvas to reflect changes
        action_canvas.update_idletasks()
    # Function to add an action
    def add_action(self,action_type="Sleep", action_value=""):
        global action_add_run_times
        if action_add_run_times == 0:
            action_type = "Hotkey"
        if action_type == "Hotkey":
            action_add_run_times = 0

        def action_delete():
            global action_add_run_times
            # Check if there are actions to delete
            if action_add_run_times > 1:
                # Remove the last action frame from the GUI
                action_single_frame[-1].destroy()
                # Decrement the run time index
                action_add_run_times -= 1
                # Remove the corresponding entries from the lists
                del action_type_comboboxes[-1]
                del action_value_entries[-1]
                del action_single_frame[-1]
            else:
                display_message("cannot delete Hotkey")
            # Reconfigure the canvas and update its position
            on_configure(None)

        if action_add_run_times >= 999:
            display_message("reached the maximum number of actions")
            return

        action_add_run_times += 1

        new_action_frame = tk.Frame(action_frame)
        new_action_frame.grid(row=len(action_type_comboboxes) + 1, column=0, sticky="ew")
        action_single_frame.append(new_action_frame)

        new_action_label = tk.Label(new_action_frame, text=f"{action_add_run_times:03}")
        new_action_label.grid(row=0, column=0)

        new_action_type_combobox = tk.StringVar()
        new_action_type_combobox.set(action_type)  # Default Selection
        if action_type == "Hotkey":
            new_action_type_option_menu = tk.OptionMenu(new_action_frame, new_action_type_combobox, "Hotkey")
        else:
            new_action_type_option_menu = tk.OptionMenu(new_action_frame, new_action_type_combobox,
                                                        "Sleep",                "Mouse Click",
                                                        "Mouse Double Click",   "Mouse Press",
                                                        "Mouse Release",        "Absolute Mouse Move", 
                                                        "Mouse Move",           "Mouse Wheel",
                                                        "Keyboard Send",        "Keyboard Write",
                                                        "Keyboard Press",       "Keyboard Release")
        new_action_type_option_menu.config(width=20)
        new_action_type_option_menu.grid(row=0, column=1, sticky="w")

        new_action_value_entry = tk.Entry(new_action_frame, width=25)
        new_action_value_entry.grid(row=0, column=2, sticky="e")
        new_action_value_entry.insert(0, action_value)  # Default Value

        new_action_delete_button = tk.Button(manager_frame, text="X", command=action_delete)
        new_action_delete_button.grid(row=4, columnspan=10, sticky="s")

        new_action_frame.grid_columnconfigure(0, weight=1)
        new_action_frame.grid_columnconfigure(1, weight=1)

        action_type_comboboxes.append(new_action_type_combobox)
        action_value_entries.append(new_action_value_entry)

        on_configure(None)  # Update the canvas and action frame position
        action_canvas.yview_moveto(1.0)
    # Function to load saved actions
  
    # Function to create Layout of GUI
    def create_widgets(self):
        self.manager_frame = tk.Frame(self.root)
        self.manager_frame.grid(row=2, column=0, sticky="n", pady=10, padx=(10, 0))
        self.manager_frame.grid_rowconfigure(0, weight=1)
        self.manager_frame.grid_columnconfigure(0, weight=1)

        self.separator_2 = ttk.Separator(self.root, orient="vertical")
        self.separator_2.grid(row=2, column=3, sticky="ns", padx=10)

        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.grid(row=2, column=4, sticky="n", pady=10, padx=(0, 10))
        self.terminal_frame.grid_rowconfigure(0, weight=1)
        self.terminal_frame.grid_columnconfigure(0, weight=1)

        self.control_frame = tk.Frame(self.manager_frame)
        self.control_frame.grid(row=0, column=0, padx=10, pady=(0, 10))

        self.action_canvas = tk.Canvas(self.manager_frame)
        self.action_canvas.grid(row=3, column=0)

        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.action_canvas.yview)
        self.scrollbar.grid(row=2, column=1, sticky="ns")

        self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"), yscrollcommand=self.scrollbar.set)
        self.action_canvas.bind("<Configure>", self.on_configure)

        self.action_frame = tk.Frame(self.action_canvas)
        self.action_frame_place = self.action_canvas.create_window((0, 0), window=self.action_frame, anchor="n")

        self.add_action_button = tk.Button(self.control_frame, text="Add Action", command=self.add_action)
        self.add_action_button.grid(row=1, column=0, columnspan=2)

        self.save_button = tk.Button(self.control_frame, text="Save Actions", command=save.save_creator)
        self.save_button.grid(row=0, column=1)

        self.Load_button = tk.Button(self.control_frame, text="Load Actions", command=self.Load_actions)
        self.Load_button.grid(row=0, column=0)

        self.execution_frame = tk.Frame(self.terminal_frame)
        self.execution_frame.grid(row=0, column=0)

        self.terminal_label = tk.Label(self.terminal_frame,text="Terminal:")
        self.terminal_label.grid(row=1, column=0, sticky="w")

        self.terminal = scrolledtext.ScrolledText(self.terminal_frame, wrap=tk.WORD, state=tk.DISABLED, width=75, height=10)
        self.terminal.grid(row=2, column=0, sticky="n")
            
        self.start_button = tk.Button(self.execution_frame, text="Start",command=Hotkey_main_instance.start_programm)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = tk.Button(self.execution_frame, text="Stop",command=Hotkey_main_instance.stop_programm)

# Create the main Tkinter window
root = tk.Tk()
app = Hotkey_Manager(root)
save = save_action_set()

# Ensure smooth exit
atexit.register(Hotkey_main_instance.at_exit)
# Load exported data
exported_data.update(Load_exported_data())
# Create an instance of Optionmenu_Hotkey_Choice
Optionmenu_Hotkey_Choice_Instance = Optionmenu_Hotkey_Choice.create_instance(execution_frame, exported_data)


root.mainloop()



        