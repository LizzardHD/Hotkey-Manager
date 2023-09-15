
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import json
import threading
import atexit
from Hotkey_Stable_v2 import Hotkey
from typing import Callable
import keyboard
import mouse
import time

# Lists to store action type comboboxes, action value entries, and action frames
action_type_comboboxes = []
action_value_entries = []
action_single_frame = []

# Dictionary to store exported data
exported_data = {}

# Variables for managing action sets
action_set_name = ""
action_add_run_times = 0
display_message_run_times = 0

# Variables for starting and stopping the Hotkey
hotkey_switch = False
stop_command = False

# Function to add a hotkey with a loop
def Hotkey(actionlist:type[list],printer: Callable):
    running = False
    falling_trigger = False
    for action in actionlist:
        if action[0] == "Hotkey":
            myhotkey = action[1]
            break

    def loop_function():
        global hotkey_switch
        while running:
            if hotkey_switch == True:
                print("loop")
                for key, value in actionlist:
                    if key == "Sleep":
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
            else:
                print(hotkey_switch)
                output_loop.join()
                keyboard.unhook_all()
                return

    def on_hotkey_event(e):
        nonlocal running, falling_trigger

        if e.event_type == keyboard.KEY_DOWN:
            if not falling_trigger:
                running = not running
                falling_trigger = True
                if running:
                    try:
                        output_loop.start()
                    except:
                        pass
                    finally:
                        printer("Loop started")
                else:
                    try:
                        output_loop.daemon = True
                    except:
                        pass
                    finally:
                        printer("Loop stopped")

        elif e.event_type == keyboard.KEY_UP:
            falling_trigger = False

    printer("Press %s to start/stop the loop." % myhotkey)
    output_loop = threading.Thread(target=loop_function)
    if hotkey_switch:
        keyboard.on_press_key(myhotkey, on_hotkey_event)
        keyboard.on_release_key(myhotkey, on_hotkey_event)
    


# Function to display a message in the terminal
def display_message(message):
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
def save_exported_data():
    with open("exported_data.json", "w") as json_file:
        json.dump(exported_data, json_file)
    update_option_menu()

# Function to load exported data from a JSON file
def Load_exported_data():
    try:
        with open("exported_data.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}

def update_option_menu():
    # Clear the existing options
    name_option['menu'].delete(0, 'end')
    # Update the list of action set names
    action_set_names = list(exported_data.keys())
    for name in action_set_names:
        name_option['menu'].add_command(label=name, command=tk._setit(name_key, name))


def exit_handler():
    global hotkey_switch
    hotkey_switch = False
    return

def programm_run_switch():
    global hotkey_switch, stop_command

    # Get the selected name (key) from the OptionMenu
    selected_name = name_key.get()

    if not selected_name:
        display_message("Please select a name from the list.")
        return
    
    if hotkey_switch:
        # State Switch
        hotkey_switch = False
        stop_command = True
        display_message(f"{selected_name} stopped")
        # Button Switch
        start_button.grid(row=0, column=0, padx=5)
        stop_button.grid_forget()
    else:
        # State Switch
        hotkey_switch = True
        stop_command = False
        display_message(f"{selected_name} started")
        # Call the Function
        selected_data = exported_data.get(selected_name, [])
        Hotkey(selected_data,display_message)
        # Button Switch
        stop_button.grid(row=0, column=0, padx=5)
        start_button.grid_forget()
    

    terminal_frame.update_idletasks


# Function to update the canvas and action frame position
def on_configure(event=None):
    action_canvas.configure(scrollregion=action_canvas.bbox("all"))

    if action_canvas.winfo_width() > action_frame.winfo_reqwidth():
        x_position = (action_canvas.winfo_width() - action_frame.winfo_reqwidth()) / 2 + action_frame.winfo_reqwidth() / 2
        action_canvas.coords(action_frame_place, x_position, 0)
    else:
        x_position = action_canvas.winfo_width() / 2
        action_canvas.coords(action_frame_place, x_position, 0)

    total_child_height = sum(child.winfo_reqheight() for child in action_frame.winfo_children())
    action_canvas.config(height=min(300, total_child_height))

    if action_frame.winfo_reqheight() > action_canvas.winfo_height():
        scrollbar.grid(row=2, column=1, sticky="ns")
        action_canvas.config(scrollregion=action_canvas.bbox("all"))
    else:
        scrollbar.grid_remove()
        action_canvas.config(scrollregion=action_canvas.bbox("all"))

    update_option_menu()
    action_canvas.update_idletasks()


# Function to add an action
def add_action(action_type="Sleep", action_value=""):
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
                                                    "Sleep", "Mouse Click",
                                                    "Mouse Double Click", "Mouse Press",
                                                    "Mouse Release", "Mouse Move", "Mouse Wheel",
                                                    "Keyboard Send", "Keyboard Write",
                                                    "Keyboard Press", "Keyboard Release")
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
def Load_actions():
    def import_data():
        selected_name = import_name_var.get()
        imported_data = exported_data.get(selected_name, [])

        if imported_data:
            # Clear the existing GUI actions
            for frame in action_frame.winfo_children():
                frame.destroy()
            action_type_comboboxes.clear()
            action_value_entries.clear()
            # Check if the first action is "Hotkey"
            if imported_data[0][0] != "Hotkey":
                # If not, add an empty "Hotkey" action at index 0
                imported_data.insert(0, ["Hotkey", ""])
            # Create new action frames based on imported data
            for action_type, action_value in imported_data:
                add_action(action_type, action_value)
            global action_set_name
            action_set_name = selected_name
        else:
            display_message(f"No data found for name: {selected_name}")

        # Close the Load window
        Load_window.destroy()

    def delete_action_set():
        selected_name = import_name_var.get()
        if selected_name in exported_data:
            del exported_data[selected_name]
            save_exported_data()
            display_message(f"Deleted action set '{selected_name}'")
            # Clear the name selection
            import_name_var.set("")
            # Give Feedback
            Data_deleted = tk.Label(Load_window, text=f"{selected_name} deleted")
            Data_deleted.grid(row=0, columnspan=2)
            # Clear the existing options
            Load_option_menu['menu'].delete(0, 'end')
            # Update the list of import names and recreate the OptionMenu
            import_names = list(exported_data.keys())
            for name in import_names:
                Load_option_menu['menu'].add_command(label=name, command=tk._setit(import_name_var, name))
        else:
            display_message(f"No action set found for name: {selected_name}")

    # Load previously exported data
    exported_data.update(Load_exported_data())

    # Create a new window for importing data
    Load_window = tk.Frame(manager_frame)
    Load_window.grid(row=2, padx=10, pady=(0, 10))

    # Add an OptionMenu to select the name/key
    import_name_var = tk.StringVar()
    import_name_var.set("")  # Default selection
    import_names = list(exported_data.keys())
    try:
        Load_option_menu = tk.OptionMenu(Load_window, import_name_var, *import_names)
        Load_option_menu.grid(row=1, columnspan=2)
        Load_option_menu.config(width=25)
        # Add a "Load" button
        Load_button = tk.Button(Load_window, text="Load", command=import_data)
        Load_button.grid(row=2, column=1, sticky="w")
        # Add a "Delete" button
        delete_button = tk.Button(Load_window, text="Delete", command=delete_action_set)
        delete_button.grid(row=2, column=0, sticky="e")
    except:
        # Give Feedback
        Load_empty_list_fault = tk.Label(Load_window, text="No Data")
        Load_empty_list_fault.grid(row=0, columnspan=2)
    finally:
        # Add a "Close" button
        close_button = tk.Button(Load_window, text="Close", command=Load_window.destroy)
        close_button.grid(row=3, columnspan=2)
    update_option_menu()

# Function to save the current actions
def save_actions():
    exported_data.update(Load_exported_data())
    action_values = []
    for each in range(len(action_type_comboboxes)):
        action_type = action_type_comboboxes[each].get()
        action_value = action_value_entries[each].get()
        action_values.append((action_type, action_value))

    # Create a new window for exporting data
    save_window = tk.Frame(manager_frame)
    save_window.grid(row=5, padx=10, pady=10)

    # Add a Label and an Entry widget to input the name
    name_label = tk.Label(save_window, text="Enter a name for this action set:")
    name_label.grid()

    name_entry = tk.Entry(save_window)
    name_entry.insert(0, action_set_name)
    name_entry.grid(pady=(0, 5))

    def save_with_name():
        name = name_entry.get()
        if name:
            exported_data[name] = action_values
            save_exported_data()
            display_message(f"{name}={list(exported_data[name])}")
            save_window.destroy()
        else:
            display_message("Please enter a name.")

    # Add an "Enter" button to confirm the name
    enter_button = tk.Button(save_window, text="Enter", command=save_with_name)
    enter_button.grid()

atexit.register(exit_handler)
# Create the main Tkinter window
root = tk.Tk()
root.title("Hotkey Handler")
root.resizable(False, False)
root.columnconfigure(0, weight=1)

# Create frames for organizing UI elements
manager_frame = tk.Frame(root)
manager_frame.grid(row=2, column=0, sticky="n", pady=10, padx=(10, 0))
manager_frame.grid_rowconfigure(0, weight=1)
manager_frame.grid_columnconfigure(0, weight=1)

separator_2 = ttk.Separator(root, orient="vertical")
separator_2.grid(row=2, column=3, sticky="ns", padx=10)

terminal_frame = tk.Frame(root)
terminal_frame.grid(row=2, column=4, sticky="n", pady=10, padx=(0, 10))
terminal_frame.grid_rowconfigure(0, weight=1)
terminal_frame.grid_columnconfigure(0, weight=1)

control_frame = tk.Frame(manager_frame)
control_frame.grid(row=0, column=0, padx=10, pady=(0, 10))

action_canvas = tk.Canvas(manager_frame)
action_canvas.grid(row=3, column=0)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=action_canvas.yview)
scrollbar.grid(row=2, column=1, sticky="ns")

action_canvas.config(scrollregion=action_canvas.bbox("all"), yscrollcommand=scrollbar.set)
action_canvas.bind("<Configure>", on_configure)

# Create the action frame inside the canvas
action_frame = tk.Frame(action_canvas)
action_frame_place = action_canvas.create_window((0, 0), window=action_frame, anchor="n")

add_action_button = tk.Button(control_frame, text="Add Action", command=add_action)
add_action_button.grid(row=1, column=0, columnspan=2)

save_button = tk.Button(control_frame, text="Save Actions", command=save_actions)
save_button.grid(row=0, column=1)

Load_button = tk.Button(control_frame, text="Load Actions", command=Load_actions)
Load_button.grid(row=0, column=0)

execution_frame = tk.Frame(terminal_frame)
execution_frame.grid(row=0, column=0)

terminal_label = tk.Label(terminal_frame,text="Terminal:")
terminal_label.grid(row=1, column=0, sticky="w")

terminal = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, state=tk.DISABLED, width=75, height=10)
terminal.grid(row=2, column=0, sticky="n")
    
start_button = tk.Button(execution_frame, text="Start",command=programm_run_switch)
start_button.grid(row=0, column=0, padx=5)
stop_button = tk.Button(execution_frame, text="Stop",command=programm_run_switch)

# Load exported data
exported_data.update(Load_exported_data())

name_key = tk.StringVar()
name_key.set(" ")
name_option = tk.OptionMenu(execution_frame, name_key,*list(exported_data.keys()),command=exported_data.update(Load_exported_data()))
name_option.grid(row=1, column=0, pady=10)
name_option.config(width=25)

root.mainloop()