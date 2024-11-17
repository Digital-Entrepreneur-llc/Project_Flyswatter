# run_lights.py

import keyboard
import subprocess

def run_script_flyswatter():
    # Path to the lights.py script
    script_path_flyswatter = "C:\\Users\\benja\\Desktop\\flyswatter_macro.py"
    # Run the script using subprocess
    subprocess.run(["python", script_path_flyswatter])

def run_script_kill():
    # Path to the kill.py script
    script_path_kill = "C:\\Users\\benja\\Desktop\\kill.py"
    # Run the script using subprocess
    subprocess.run(["python", script_path_kill])

# Set up a keyboard hotkey
keyboard.add_hotkey('c', run_script_flyswatter)
keyboard.add_hotkey('a', run_script_kill)

# Wait indefinitely until "esc" is pressed
keyboard.wait('esc')
