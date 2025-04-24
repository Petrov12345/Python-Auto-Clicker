import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import keyboard
import time

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("320x280")  # Reduced width to remove dead space
        self.is_running = False
        self.hotkey = "f6"

        # Set background color for the entire window
        self.root.configure(bg="#2C3E50")

        # Create the sidebar for buttons
        self.create_sidebar()

        # Create the input section
        self.create_time_input()

        # Hotkey binding
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

        # Handle window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_sidebar(self):
        """Creates a stylish sidebar with buttons."""
        # Sidebar for buttons
        sidebar = tk.Frame(self.root, bg="#34495E", width=120, height=300)
        sidebar.place(x=0, y=0)

        # Start button (Green) - Enlarge to match Change Hotkey button size
        self.start_button = tk.Button(sidebar, text="Start", bg="#27AE60", fg="white", font=("Helvetica", 12, "bold"), command=self.start_clicking)
        self.start_button.pack(pady=15, ipadx=35, ipady=10)  # Match the padding of Change Hotkey button

        # Stop button (Red) - Enlarge to match Change Hotkey button size
        self.stop_button = tk.Button(sidebar, text="Stop", bg="#C0392B", fg="white", font=("Helvetica", 12, "bold"), command=self.stop_clicking)
        self.stop_button.pack(pady=15, ipadx=35, ipady=10)  # Match the padding of Change Hotkey button

        # Change Hotkey button (Blue) - No changes needed, as it already has the correct size
        self.change_hotkey_button = tk.Button(sidebar, text="Change Hotkey", bg="#2980B9", fg="white", font=("Helvetica", 10, "bold"), command=self.start_hotkey_recording)
        self.change_hotkey_button.pack(pady=18, ipadx=5, ipady=10)

        # Initially disable the Stop button
        self.disable_button(self.stop_button, fade_color="#E74C3C")

    def create_time_input(self):
        """Creates the time input section with a sleek modern design."""
        # Input frame for the entry fields and labels (adjusted to remove dead space)
        input_frame = tk.Frame(self.root, bg="#34495E")
        input_frame.place(x=140, y=50, width=180, height=180)  # Reduced width to remove dead space

        # Time labels and input boxes with updated styles
        self.min_label = tk.Label(input_frame, text="Minutes:", bg="#34495E", fg="white", font=("Helvetica", 12))
        self.min_label.grid(row=0, column=0, padx=5, pady=10)
        self.min_entry = tk.Entry(input_frame, width=5, bg="#95A5A6", fg="white", font=("Helvetica", 12))
        self.min_entry.grid(row=0, column=1, padx=5, pady=10)

        self.sec_label = tk.Label(input_frame, text="Seconds:", bg="#34495E", fg="white", font=("Helvetica", 12))
        self.sec_label.grid(row=1, column=0, padx=5, pady=10)
        self.sec_entry = tk.Entry(input_frame, width=5, bg="#95A5A6", fg="white", font=("Helvetica", 12))
        self.sec_entry.grid(row=1, column=1, padx=5, pady=10)

        self.milli_label = tk.Label(input_frame, text="Milliseconds:", bg="#34495E", fg="white", font=("Helvetica", 12))
        self.milli_label.grid(row=2, column=0, padx=5, pady=10)
        self.milli_entry = tk.Entry(input_frame, width=5, bg="#95A5A6", fg="white", font=("Helvetica", 12))
        self.milli_entry.grid(row=2, column=1, padx=5, pady=10)

        # Add the status and current hotkey labels below the time inputs, centered
        self.hotkey_label = tk.Label(input_frame, text=f"Current Hotkey: {self.hotkey}", fg="white", bg="#34495E", font=("Helvetica", 12))
        self.hotkey_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.status_label = tk.Label(input_frame, text="Status: Stopped", fg="white", bg="#34495E", font=("Helvetica", 12, "bold"))
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def start_clicking(self):
        """Start the clicking thread."""
        if not self.is_running:
            self.is_running = True
            self.hotkey_label.config(text="Auto Clicker Running...")
            self.status_label.config(text="Status: Running", bg="#27AE60")
            thread = threading.Thread(target=self.click_loop)
            thread.start()

            # Disable Start button and enable Stop button
            self.disable_button(self.start_button, fade_color="#82E0AA")
            self.enable_button(self.stop_button)

    def stop_clicking(self):
        """Stop the clicking thread."""
        self.is_running = False
        self.hotkey_label.config(text=f"Current Hotkey: {self.hotkey}")
        self.status_label.config(text="Status: Stopped", bg="#C0392B")

        # Enable Start button and disable Stop button
        self.enable_button(self.start_button)
        self.disable_button(self.stop_button, fade_color="#E74C3C")

    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def click_loop(self):
        try:
            # Handle minutes, seconds, and milliseconds input
            min_delay = int(self.min_entry.get()) * 60 if self.min_entry.get().isdigit() else 0
            sec_delay = int(self.sec_entry.get()) if self.sec_entry.get().isdigit() else 0
            milli_delay = float(self.milli_entry.get()) / 1000 if self.milli_entry.get() else 0  # Convert to seconds

            total_delay = min_delay + sec_delay + milli_delay

            # Validate minimum delay (for practical limits on most systems)
            if total_delay < 0.0001:  # About 0.1 ms
                self.hotkey_label.config(text="Minimum delay is 0.1 ms")
                return
        except ValueError:
            self.hotkey_label.config(text="Enter valid numbers!")
            return

        # Event to control the stopping of the loop
        stop_event = threading.Event()

        def click():
            while self.is_running and not stop_event.is_set():
                start_time = time.perf_counter()  # High-precision timer start
                pyautogui.click()
                elapsed = time.perf_counter() - start_time
                time_to_wait = max(0, total_delay - elapsed)  # Ensure it doesn't sleep negative time
                stop_event.wait(time_to_wait)  # Replaces time.sleep() for more precise timing

        click_thread = threading.Thread(target=click)
        click_thread.start()

    def start_hotkey_recording(self):
        """Capture new hotkey from user keypress."""
        self.hotkey_label.config(text="Press a key to set new hotkey...")
        self.root.unbind_all("<Key>")
        self.root.bind("<Key>", self.set_new_hotkey)

    def set_new_hotkey(self, event):
        """Set a new hotkey from the user's input."""
        new_hotkey = event.keysym.lower()
        keyboard.remove_hotkey(self.hotkey)  # Remove the old hotkey binding
        self.hotkey = new_hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)  # Set the new hotkey binding
        self.hotkey_label.config(text=f"New Hotkey: {self.hotkey}")
        messagebox.showinfo("Hotkey Changed", f"New Hotkey: {self.hotkey}")  # Confirmation message
        self.root.unbind("<Key>")  # Unbind key capture

    def unfocus_entries(self, event):
        """Unfocus the entry fields when clicking outside."""
        widget = event.widget
        if widget not in (self.min_entry, self.sec_entry, self.milli_entry):
            self.root.focus()

    def disable_button(self, button, fade_color):
        """Disable a button and change its color to indicate it's disabled."""
        button.config(state=tk.DISABLED, bg=fade_color)

    def enable_button(self, button):
        """Enable a button and restore its original color."""
        if button == self.start_button:
            button.config(state=tk.NORMAL, bg="#27AE60")
        elif button == self.stop_button:
            button.config(state=tk.NORMAL, bg="#C0392B")

    def on_closing(self):
        """Ensure the application stops clicking when closed."""
        self.stop_clicking()
        self.root.destroy()

# Main loop
root = tk.Tk()
app = AutoClickerApp(root)
root.mainloop()
