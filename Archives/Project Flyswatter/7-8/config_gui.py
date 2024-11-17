import tkinter as tk
from tkinter import messagebox
import configparser

def save_config():
    try:
        known_lat = float(known_lat_entry.get())
        known_lon = float(known_lon_entry.get())
        heading = float(heading_entry.get())
        left_boundary = float(left_boundary_entry.get())
        right_boundary = float(right_boundary_entry.get())
        min_altitude = float(min_altitude_entry.get())
        max_altitude = float(max_altitude_entry.get())
    except ValueError:
        messagebox.showwarning("Warning", "All fields must be filled out with valid numbers")
        return

    config = configparser.ConfigParser()
    config['Settings'] = {
        'known_latitude': known_lat,
        'known_longitude': known_lon,
        'heading': heading,
        'left_boundary': left_boundary,
        'right_boundary': right_boundary,
        'min_altitude': min_altitude,
        'max_altitude': max_altitude
    }

    try:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Info", "Configuration saved successfully!")
        root.destroy()  # Close the main window
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

# Create the main window
root = tk.Tk()
root.title("Flyswatter Configuration")

# Create and place labels and entry fields
tk.Label(root, text="HPM's Latitude (Decimal Degrees)").grid(row=0, column=0, padx=10, pady=5)
known_lat_entry = tk.Entry(root)
known_lat_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="HPM's Longitude (Decimal Degrees)").grid(row=1, column=0, padx=10, pady=5)
known_lon_entry = tk.Entry(root)
known_lon_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="HPM's Heading (degrees)").grid(row=2, column=0, padx=10, pady=5)
heading_entry = tk.Entry(root)
heading_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Flyswatter's Left Limit (degrees)").grid(row=3, column=0, padx=10, pady=5)
left_boundary_entry = tk.Entry(root)
left_boundary_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Flyswatter's Right Limit (degrees)").grid(row=4, column=0, padx=10, pady=5)
right_boundary_entry = tk.Entry(root)
right_boundary_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Minimum Altitude (meters, MSL)").grid(row=5, column=0, padx=10, pady=5)
min_altitude_entry = tk.Entry(root)
min_altitude_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Maximum Altitude (meters, MSL)").grid(row=6, column=0, padx=10, pady=5)
max_altitude_entry = tk.Entry(root)
max_altitude_entry.grid(row=6, column=1, padx=10, pady=5)

# Create and place the save button
save_button = tk.Button(root, text="Save", command=save_config)
save_button.grid(row=7, column=0, columnspan=2, pady=10)

# Start the main event loop
root.mainloop()