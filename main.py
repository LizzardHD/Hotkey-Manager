import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import json
import threading
import atexit
from typing import Callable, List, Tuple
import keyboard
import mouse
import time

from enum import Enum


class ActionType(Enum): # string to enum must be possible
	HOTKEY = "Hotkey"
	SLEEP = "Sleep"


class HotkeyApp:
	def __init__(self):
		self.root = None

		# Lists to store action type comboboxes, action value entries, and action frames
		self.action_type_comboboxes = []
		self.action_value_entries = []
		self.action_single_frame = []

		# Dictionary to store exported data
		self.exported_data = dict()

		# Variables for managing action sets
		self.action_set_name = ""
		self.action_add_run_times = 0
		self.display_message_run_times = 0

		# Variables for starting and stopping the Hotkey
		self.hotkey_switch = False
		self.stop_command = False

		# Tkinter elements
		self.manager_frame = None
		self.terminal = None
		self.terminal_frame = None
		self.action_frame = None
		self.action_canvas = None
		self.action_frame_place = None
		self.scrollbar = None

		self.start_button = None
		self.stop_button = None
		self.name_key = None

		self.name_option = None
		self.load_window = None
		self.load_option_menu = None

	# === build & run ===

	def build(self):
		self.root = tk.Tk()
		self.root.title("Hotkey Handler")
		self.root.resizable(False, False)
		self.root.columnconfigure(0, weight=1)

		# Create frames for organizing UI elements
		self.manager_frame = tk.Frame(self.root)
		self.manager_frame.grid(row=2, column=0, sticky="n", pady=10, padx=(10, 0))
		self.manager_frame.grid_rowconfigure(0, weight=1)
		self.manager_frame.grid_columnconfigure(0, weight=1)

		separator_2 = ttk.Separator(self.root, orient="vertical")
		separator_2.grid(row=2, column=3, sticky="ns", padx=10)

		self.terminal_frame = tk.Frame(self.root)
		self.terminal_frame.grid(row=2, column=4, sticky="n", pady=10, padx=(0, 10))
		self.terminal_frame.grid_rowconfigure(0, weight=1)
		self.terminal_frame.grid_columnconfigure(0, weight=1)

		control_frame = tk.Frame(self.manager_frame)
		control_frame.grid(row=0, column=0, padx=10, pady=(0, 10))

		self.action_canvas = tk.Canvas(self.manager_frame)
		self.action_canvas.grid(row=3, column=0)

		self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.action_canvas.yview)
		self.scrollbar.grid(row=2, column=1, sticky="ns")

		self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"), yscrollcommand=self.scrollbar.set)
		self.action_canvas.bind("<Configure>", self._on_configure)

		# Create the action frame inside the canvas
		self.action_frame = tk.Frame(self.action_canvas)
		self.action_frame_place = self.action_canvas.create_window((0, 0), window=self.action_frame, anchor="n")

		add_action_button = tk.Button(control_frame, text="Add Action", command=self._add_action)
		add_action_button.grid(row=1, column=0, columnspan=2)

		save_button = tk.Button(control_frame, text="Save Actions", command=self._save_actions)
		save_button.grid(row=0, column=1)

		Load_button = tk.Button(control_frame, text="Load Actions", command=self._load_actions)
		Load_button.grid(row=0, column=0)

		execution_frame = tk.Frame(self.terminal_frame)
		execution_frame.grid(row=0, column=0)

		terminal_label = tk.Label(self.terminal_frame, text="Terminal:")
		terminal_label.grid(row=1, column=0, sticky="w")

		self.terminal = scrolledtext.ScrolledText(self.terminal_frame, wrap=tk.WORD, state=tk.DISABLED, width=75, height=10)
		self.terminal.grid(row=2, column=0, sticky="n")

		self.start_button = tk.Button(execution_frame, text="Start", command=self._program_run_switch)
		self.start_button.grid(row=0, column=0, padx=5)
		self.stop_button = tk.Button(execution_frame, text="Stop", command=self._program_run_switch)

		# Load exported data
		self.exported_data.update(self._load_exported_data())

		self.name_key = tk.StringVar()
		self.name_key.set(" ")
		self.name_option = tk.OptionMenu(
			execution_frame,
			self.name_key,
			*list(self.exported_data.keys()),
			command=self.exported_data.update(self._load_exported_data()) # weird, why is this a function call?
		)
		self.name_option.grid(row=1, column=0, pady=10)
		self.name_option.config(width=25)

	def run(self):
		self.root.mainloop()

	def _program_run_switch(self):
		global hotkey_switch, stop_command

		# Get the selected name (key) from the OptionMenu
		selected_name = self.name_key.get()

		if not selected_name:
			self._display_message("Please select a name from the list.")
			return

		if hotkey_switch:
			# State Switch
			hotkey_switch = False
			stop_command = True
			self._display_message(f"{selected_name} stopped")
			# Button Switch
			self.start_button.grid(row=0, column=0, padx=5)
			self.stop_button.grid_forget()
		else:
			# State Switch
			hotkey_switch = True
			stop_command = False
			self._display_message(f"{selected_name} started")
			# Call the Function
			selected_data = self.exported_data.get(selected_name, [])
			HotkeySequence(self, selected_data, self._display_message)
			# Button Switch
			self.stop_button.grid(row=0, column=0, padx=5)
			self.start_button.grid_forget()

		self.terminal_frame.update_idletasks # TODO: soll nicht executed werden?

	# === Action Editing ===

	def _add_action(self, action_type: ActionType = ActionType.SLEEP, action_value = ""):
		global action_add_run_times
		if action_add_run_times == 0:
			action_type = ActionType.HOTKEY
		if action_type == ActionType.HOTKEY:
			action_add_run_times = 0

		if action_add_run_times >= 999:
			self._display_message("reached the maximum number of actions")
			return

		action_add_run_times += 1

		new_action_frame = tk.Frame(self.action_frame)
		new_action_frame.grid(row=len(self.action_type_comboboxes) + 1, column=0, sticky="ew")
		self.action_single_frame.append(new_action_frame)

		new_action_label = tk.Label(new_action_frame, text=f"{action_add_run_times:03}")
		new_action_label.grid(row=0, column=0)

		new_action_type_combobox = tk.StringVar()
		new_action_type_combobox.set(action_type.value())  # Default Selection
		if action_type == ActionType.HOTKEY:
			new_action_type_option_menu = tk.OptionMenu(new_action_frame, new_action_type_combobox, ActionType.HOTKEY.value())
		else:
			new_action_type_option_menu = tk.OptionMenu(new_action_frame, new_action_type_combobox,
														"Sleep", "Mouse Click",
														"Mouse Double Click", "Mouse Press",
														"Mouse Release", "Mouse Move", "Mouse Wheel",
														"Keyboard Send", "Keyboard Write",
														"Keyboard Press", "Keyboard Release") # TODO: enumerate over actiontype neum and create this list
		new_action_type_option_menu.config(width=20)
		new_action_type_option_menu.grid(row=0, column=1, sticky="w")

		new_action_value_entry = tk.Entry(new_action_frame, width=25)
		new_action_value_entry.grid(row=0, column=2, sticky="e")
		new_action_value_entry.insert(0, action_value)  # Default Value

		new_action_delete_button = tk.Button(self.manager_frame, text="X", command=self.__action_delete)
		new_action_delete_button.grid(row=4, columnspan=10, sticky="s")

		new_action_frame.grid_columnconfigure(0, weight=1)
		new_action_frame.grid_columnconfigure(1, weight=1)

		self.action_type_comboboxes.append(new_action_type_combobox)
		self.action_value_entries.append(new_action_value_entry)

		self._on_configure(None)  # Update the canvas and action frame position
		self.action_canvas.yview_moveto(1.0)

	def __action_delete(self):
		global action_add_run_times
		# Check if there are actions to delete
		if action_add_run_times > 1:
			# Remove the last action frame from the GUI
			self.action_single_frame[-1].destroy()
			# Decrement the run time index
			action_add_run_times -= 1
			# Remove the corresponding entries from the lists
			del self.action_type_comboboxes[-1]
			del self.action_value_entries[-1]
			del self.action_single_frame[-1]
		else:
			self._display_message("cannot delete Hotkey")
		# Reconfigure the canvas and update its position
		self._on_configure(None)

	# === Update Handlers ===

	def _update_option_menu(self):
		# Clear the existing options
		self.name_option['menu'].delete(0, 'end')
		# Update the list of action set names
		action_set_names = list(self.exported_data.keys())
		for name in action_set_names:
			self.name_option['menu'].add_command(label=name, command=tk._setit(self.name_key, name))

	def _on_configure(self, event = None):
		self.action_canvas.configure(scrollregion=self.action_canvas.bbox("all"))

		if self.action_canvas.winfo_width() > self.action_frame.winfo_reqwidth():
			x_position = (self.action_canvas.winfo_width() - self.action_frame.winfo_reqwidth()) / 2 + self.action_frame.winfo_reqwidth() / 2
			self.action_canvas.coords(self.action_frame_place, x_position, 0)
		else:
			x_position = self.action_canvas.winfo_width() / 2
			self.action_canvas.coords(self.action_frame_place, x_position, 0)

		total_child_height = sum(child.winfo_reqheight() for child in self.action_frame.winfo_children())
		self.action_canvas.config(height=min(300, total_child_height))

		if self.action_frame.winfo_reqheight() > self.action_canvas.winfo_height():
			self.scrollbar.grid(row=2, column=1, sticky="ns")
			self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"))
		else:
			self.scrollbar.grid_remove()
			self.action_canvas.config(scrollregion=self.action_canvas.bbox("all"))

		self._update_option_menu()
		self.action_canvas.update_idletasks()

	# === Save / Load ===

	def _load_actions(self):
		# Load previously exported data
		self.exported_data.update(self._load_exported_data())

		# Create a new window for importing data
		self.load_window = tk.Frame(self.manager_frame)
		self.load_window.grid(row=2, padx=10, pady=(0, 10))

		# Add an OptionMenu to select the name/key
		import_name_var = tk.StringVar()
		import_name_var.set("")  # Default selection
		import_names = list(self.exported_data.keys())
		try:
			self.load_option_menu = tk.OptionMenu(self.load_window, import_name_var, *import_names)
			self.load_option_menu.grid(row=1, columnspan=2)
			self.load_option_menu.config(width=25)
			# Add a "Load" button
			Load_button = tk.Button(self.load_window, text="Load", command=self.__import_data(import_name_var))
			Load_button.grid(row=2, column=1, sticky="w")
			# Add a "Delete" button
			delete_button = tk.Button(self.load_window, text="Delete", command=self.__delete_action_set(import_name_var))
			delete_button.grid(row=2, column=0, sticky="e")
		except:
			# Give Feedback
			Load_empty_list_fault = tk.Label(self.load_window, text="No Data")
			Load_empty_list_fault.grid(row=0, columnspan=2)
		finally:
			# Add a "Close" button
			close_button = tk.Button(self.load_window, text="Close", command=self.load_window.destroy)
			close_button.grid(row=3, columnspan=2)
		self._update_option_menu()

	def __import_data(self, import_name_var: tk.StringVar):
		def __inner():
			selected_name = import_name_var.get()
			imported_data = self.exported_data.get(selected_name, [])

			if imported_data:
				# Clear the existing GUI actions
				for frame in self.action_frame.winfo_children():
					frame.destroy()
				self.action_type_comboboxes.clear()
				self.action_value_entries.clear()
				# Check if the first action is "Hotkey"
				if imported_data[0][0] != "Hotkey":
					# If not, add an empty "Hotkey" action at index 0
					imported_data.insert(0, ["Hotkey", ""])
				# Create new action frames based on imported data
				for action_type, action_value in imported_data:
					self._add_action(action_type, action_value)
				global action_set_name
				action_set_name = selected_name
			else:
				self._display_message(f"No data found for name: {selected_name}")

			# Close the Load window
			self.load_window.destroy()
		return __inner

	def __delete_action_set(self, import_name_var: tk.StringVar):
		def __inner():
			selected_name = import_name_var.get()
			if selected_name in self.exported_data:
				del self.exported_data[selected_name]
				self._save_exported_data()
				self._display_message(f"Deleted action set '{selected_name}'")
				# Clear the name selection
				import_name_var.set("")
				# Give Feedback
				Data_deleted = tk.Label(self.load_window, text=f"{selected_name} deleted")
				Data_deleted.grid(row=0, columnspan=2)
				# Clear the existing options
				self.load_option_menu['menu'].delete(0, 'end')
				# Update the list of import names and recreate the OptionMenu
				import_names = list(self.exported_data.keys())
				for name in import_names:
					self.load_option_menu['menu'].add_command(label=name, command=tk._setit(import_name_var, name))
			else:
				self._display_message(f"No action set found for name: {selected_name}")
		return __inner

	def _load_exported_data(self):
		try:
			with open("exported_data.json", "r") as json_file:
				return json.load(json_file)
		except FileNotFoundError:
			return {}

	def _save_exported_data(self):
		with open("exported_data.json", "w") as json_file:
			json.dump(self.exported_data, json_file)
		self._update_option_menu()

	def _save_actions(self):
		self.exported_data.update(self._load_exported_data())
		action_values = []
		for each in range(len(self.action_type_comboboxes)):
			action_type = self.action_type_comboboxes[each].get()
			action_value = self.action_value_entries[each].get()
			action_values.append((action_type, action_value))

		# Create a new window for exporting data
		save_window = tk.Frame(self.manager_frame)
		save_window.grid(row=5, padx=10, pady=10)

		# Add a Label and an Entry widget to input the name
		name_label = tk.Label(save_window, text="Enter a name for this action set:")
		name_label.grid()

		name_entry = tk.Entry(save_window)
		name_entry.insert(0, self.action_set_name)
		name_entry.grid(pady=(0, 5))

		# Add an "Enter" button to confirm the name
		enter_button = tk.Button(save_window, text="Enter", command=self.__save_with_name(name_entry, action_values, save_window))
		enter_button.grid()

	def __save_with_name(self, name_entry: tk.Entry, action_values, save_window: tk.Frame):
		def __inner():
			name = name_entry.get()
			if name:
				self.exported_data[name] = action_values
				self._save_exported_data()
				self._display_message(f"{name}={list(self.exported_data[name])}")
				save_window.destroy()
			else:
				self._display_message("Please enter a name.")
		return __inner

	# === Other ===

	def _display_message(self, msg: str):
		global display_message_run_times
		if display_message_run_times > 999:
			display_message_run_times = 0
		self.terminal.config(state=tk.NORMAL)  # Set the state to normal to allow editing
		self.terminal.insert(
			tk.END,
			f"------------------------------------{display_message_run_times:03}------------------------------------"
		)
		self.terminal.insert(tk.END, "\n")
		self.terminal.insert(tk.END, msg)  # Insert the message
		self.terminal.insert(tk.END, "\n")
		self.terminal.config(state=tk.DISABLED)  # Set the state back to disabled
		self.terminal.see(tk.END)
		display_message_run_times += 1

	def _exit_handler(self):
		global hotkey_switch
		hotkey_switch = False
		return


class HotkeySequence:
	def __init__(self, App: HotkeyApp, action_list: List[Tuple[ActionType, str]], printer: Callable):
		self.app = App

		self.action_list = action_list
		self.running = False
		self.falling_trigger = False
		self.printer = printer

		for action in action_list:
			if action[0] == ActionType.HOTKEY:
				self.myhotkey = action[1]
				break

		self.output_loop_thread = None

	def _loop_function(self):
		while self.running:
			if self.app.hotkey_switch == True:
				print("loop")
				for key, value in self.action_list:
					# TODO: use dict here to map action to according function
					if key == ActionType.SLEEP:
						try:
							value = float(value)
							time.sleep(value)
						except Exception as e: # TODO: real exception handling
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
						mouse.move(x, y, False)
					elif key == "Absolute Mouse Move":
						x, y = map(int, value.split(','))
						mouse.move(x, y, True)
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
				print(self.app.hotkey_switch)
				self.output_loop_thread.join()
				keyboard.unhook_all()
				return

	def _on_hotkey_event(self, e):
		if e.event_type == keyboard.KEY_DOWN:
			if not self.falling_trigger:
				self.running = not self.running
				falling_trigger = True
				if self.running:
					try:
						self.output_loop_thread.start()
					except:
						pass
					finally:
						self.printer("Loop started")
				else:
					try:
						self.output_loop_thread.daemon = True # TODO: ?
					except:
						pass
					finally:
						self.printer("Loop stopped")

		elif e.event_type == keyboard.KEY_UP:
			falling_trigger = False

	def run(self):
		self.printer(f"Press '{self.myhotkey}' to start/stop the loop.")
		self.output_loop_thread = threading.Thread(target=self._loop_function)
		if self.app.hotkey_switch:
			keyboard.on_press_key(self.myhotkey, self._on_hotkey_event)
			keyboard.on_release_key(self.myhotkey, self._on_hotkey_event)


if __name__ == "__main__":
	app = HotkeyApp()
	app.build()
	app.run()
