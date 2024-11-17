# Lib/Repo Importing 
import sys 
import time
import subprocess
import RPi.GPIO as GPIO

# Setting GPIO Pins as Output
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(2, GPIO.OUT)

# Determines Whether Script Execution is Execution/Callback and On/Off
def check_scripts():
    if sys.argv[0] == "lights.py":
        if sys.argv[1] == "on":
            script = "on"
            tracking = sys.argv[2]
            return script
        if sys.argv[1] == "off":
            script = "off"
            tracking = sys.argv[2]
            return script, tracking
    else:
        script = "alt"
        tracking = "alt"
        return script, tracking

# Transfers Script into Status & Updates Operator on Status
def define_status(alpha):
    if alpha == "on":
        status = "True"
        print("Waiting for Button Press")
        while alpha == "on":
            GPIO.output(4, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(4, GPIO.LOW)
            try:
                subprocess.run(['pgrep', '-lf', 'engage.py'], check=True)
                break
            except subprocess.CalledProcessError:
                pass
        return status
    if alpha == "off":
        status = "False"
        print("Out of Parameters")
        GPIO.output(2, GPIO.HIGH)
        time.sleep(4)
        GPIO.output(2, GPIO.LOW)
        return status
    if alpha == "alt":
        status = "alt"
        return status

# Function Calling
script, tracking = check_scripts()
status = define_status(script)
time.sleep(1)