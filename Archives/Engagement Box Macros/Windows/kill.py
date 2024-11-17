import tkinter as tk
from tkinter import messagebox

def on_process():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Reminder")

# Set the size of the window
root.geometry("300x150")

# Create a label with the message
message = tk.Label(root, text="KILL THE DRONES", font=("Arial", 14))
message.pack(pady=20)

# Create a button that closes the window
process_button = tk.Button(root, text="Process", command=on_process, font=("Arial", 12))
process_button.pack(pady=10)

# Run the main event loop
root.mainloop()