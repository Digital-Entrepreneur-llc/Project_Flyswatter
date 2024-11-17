# run_lights.py

import keyboard
from pynput import keyboard
import subprocess

def run_script_flyswatter():
    # Path to the flyswatter_macro.py script
    script_path_flyswatter = "/home/yourusername/Desktop/flyswatter_macro.py"
    # Run the script using subprocess
    subprocess.run(["python3", script_path_flyswatter])

def run_script_kill():
    # Path to the kill.py script
    script_path_kill = "/home/yourusername/Desktop/kill.py"
    # Run the script using subprocess
    subprocess.run(["python3", script_path_kill])

# Set up a keyboard hotkey
keyboard.add_hotkey('c', run_script_flyswatter)
keyboard.add_hotkey('a', run_script_kill)

# Wait indefinitely until "esc" is pressed
keyboard.wait('esc')
