import keyboard
import subprocess
import time
import sys
import os

# Path to the flyswatter_test.py script
flyswatter_test_path = r"C:\Users\benja\Desktop\Engagement Box Macros\flyswatter_test.py"

# Global state variable to keep track of the flyswatter result
flyswatter_result = None

def run_script_flyswatter():
    global flyswatter_result
    try:
        # Run the flyswatter_test.py script and capture the output
        result = subprocess.run([sys.executable, flyswatter_test_path], capture_output=True, text=True, check=True)
        flyswatter_result = result.stdout.strip()
        print(f"Flyswatter Result: {flyswatter_result}")
        
        if flyswatter_result == "Yes":
            print("Simulating: Green LED ON")
            print("Simulating: Red LED OFF")
        elif flyswatter_result == "No":
            print("Simulating: Red LED ON")
            print("Simulating: Green LED OFF")
        else:
            print("Unexpected response received.")
            flyswatter_result = None
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {flyswatter_test_path}: {e}")

def run_script_kill():
    global flyswatter_result
    if flyswatter_result == "Yes":
        print("Simulating: Running kill script...")
        # Simulate kill script
        time.sleep(1)
        print("Simulating: Kill script executed.")
        reset_system()
    else:
        print("Kill script not executed. Awaiting 'Yes' response.")

def reset_system():
    global flyswatter_result
    flyswatter_result = None
    print("System reset. Simulating: All LEDs OFF. Awaiting flyswatter script execution...")

def clear_lights_and_reset():
    print("Simulating: Clearing lights and resetting system...")
    reset_system()

def shutdown_system():
    print("Simulating: Shutting down system...")
    reset_system()
    print("System shutdown complete.")
    sys.exit()

# Set up keyboard hotkeys
keyboard.add_hotkey('c', run_script_flyswatter)
keyboard.add_hotkey('a', run_script_kill)
keyboard.add_hotkey('b', clear_lights_and_reset)

# Long press 'c' for shutdown
#keyboard.add_hotkey('c', lambda: shutdown_system() if keyboard.is_pressed('c') else None, suppress=True, timeout=2)

# Wait indefinitely for key input simulation
print("Press 'c' to run the flyswatter script, 'a' to run the kill script, 'b' to reset lights, and 'esc' to exit.")
keyboard.wait('esc')
print("Exiting simulation...")
