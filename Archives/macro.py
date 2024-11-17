import keyboard
import subprocess

# Define the key combinations and corresponding script paths
KEY_SCRIPT_MAPPING = {
    "shift+F1": "/home/charlie/Desktop/checkflyswatter.py",
    "shift+F2": "/home/charlie/Desktop/engage.py"
}

def on_key_event(e):
    key_combination = f"{e.name}+{'ctrl' if e.event_type == 'down' else ''}"
    if key_combination in KEY_SCRIPT_MAPPING:
        script_path = KEY_SCRIPT_MAPPING[key_combination]
        subprocess.run(["python3", script_path])

# Listen for key events
keyboard.on_press_key(on_key_event)
keyboard.on_release_key(on_key_event)

# Keep the script running
keyboard.wait("esc")