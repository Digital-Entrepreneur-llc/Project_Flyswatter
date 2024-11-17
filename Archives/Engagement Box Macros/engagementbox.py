# sudo apt-get install pigpio python3-pigpio
# pip install pynput
# pip install RPi.GPIO

import keyboard
import subprocess
import pigpio
import time

import importlib.util
import sys

# Define the path to the file
file_path = r"C:\Users\benja\Desktop\Engagement Box Macros\flyswatter_test.py"

# Load the module
spec = importlib.util.spec_from_file_location("flyswatter_test", file_path)
flyswatter_test = importlib.util.module_from_spec(spec)
sys.modules["flyswatter_test"] = flyswatter_test
spec.loader.exec_module(flyswatter_test)

# Now you can use the function
ask_drone_presence = flyswatter_test.ask_drone_presence


# GPIO pin configuration
GREEN_PIN = 17  # GPIO pin for green LED
RED_PIN = 27    # GPIO pin for red LED

# Initialize pigpio
pi = pigpio.pi()

# Set GPIO modes
pi.set_mode(GREEN_PIN, pigpio.OUTPUT)
pi.set_mode(RED_PIN, pigpio.OUTPUT)

# Global state variable to keep track of the flyswatter result
flyswatter_result = None

def run_script_flyswatter():
    global flyswatter_result
    # For testing, use the popup to get the result
    flyswatter_result = ask_drone_presence()
    print(f"Flyswatter Result: {flyswatter_result}")
    
    if flyswatter_result == "Yes":
        pi.write(GREEN_PIN, 1)  # Turn on green LED
        pi.write(RED_PIN, 0)    # Ensure red LED is off
    elif flyswatter_result == "No":
        pi.write(RED_PIN, 1)    # Turn on red LED
        pi.write(GREEN_PIN, 0)  # Ensure green LED is off

#def run_script_flyswatter():
#    global flyswatter_result
#    # Path to the flyswatter_macro.py script
#    script_path_flyswatter = "/home/yourusername/Desktop/flyswatter_macro.py"
#    try:
#        result = subprocess.run(["python3", script_path_flyswatter], capture_output=True, text=True, check=True)
#        flyswatter_result = result.stdout.strip()
#        print(f"Flyswatter Result: {flyswatter_result}")
#        
#        if flyswatter_result == "Yes":
#            pi.write(GREEN_PIN, 1)  # Turn on green LED
#            pi.write(RED_PIN, 0)    # Ensure red LED is off
#        elif flyswatter_result == "No":
#            pi.write(RED_PIN, 1)    # Turn on red LED
#            pi.write(GREEN_PIN, 0)  # Ensure green LED is off
#    except subprocess.CalledProcessError as e:
#        print(f"Failed to run {script_path_flyswatter}: {e}")

def run_script_kill():
    global flyswatter_result
    if flyswatter_result == "Yes":
        # Path to the kill.py script
        script_path_kill = "/home/yourusername/Desktop/kill.py"
        try:
            subprocess.run(["python3", script_path_kill], check=True)
            # Reset the system
            reset_system()
        except subprocess.CalledProcessError as e:
            print(f"Failed to run {script_path_kill}: {e}")

def reset_system():
    global flyswatter_result
    flyswatter_result = None
    pi.write(GREEN_PIN, 0)  # Turn off green LED
    pi.write(RED_PIN, 0)    # Turn off red LED
    print("System reset. Awaiting flyswatter script execution...")

def clear_lights_and_reset():
    print("Clearing lights and resetting system...")
    reset_system()

def shutdown_system():
    print("Shutting down system...")
    reset_system()
    # Additional shutdown logic if necessary
    pi.stop()
    exit()

# Set up keyboard hotkeys
keyboard.add_hotkey('c', run_script_flyswatter)
keyboard.add_hotkey('a', run_script_kill)
keyboard.add_hotkey('b', clear_lights_and_reset, trigger_on_release=True)

# Long press 'c' for shutdown
keyboard.add_hotkey('c', shutdown_system, suppress=True, timeout=2)

# Wait indefinitely
keyboard.wait()