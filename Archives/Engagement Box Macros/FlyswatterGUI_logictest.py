import tkinter as tk
from tkinter import messagebox

def ask_drone_presence():
    # Create a simple tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask the question and get the response
    response = messagebox.askyesno("Flyswatter Check", "Is there a drone inside the Flyswatter?")

    # Return "Yes" or "No" based on the user's response
    return "Yes" if response else "No"

if __name__ == "__main__":
    result = ask_drone_presence()
    print(f"User selected: {result}")
