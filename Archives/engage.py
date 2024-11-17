# Import necessary modules
from lights import status, tracking
import pexpect
import RPi.GPIO as GPIO
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

def login_info(beta):
    if beta == 10: # masterpi
        hostname = "masterpi@ipaddress"
        password = "1qazxsw2!QAZXSW@"
        return hostname, password
    if beta == 11: # dronea
        hostname = "dronea@ipaddress"
        password = "aquaman"
        return hostname, password
    if beta == 12: # droneb
        hostname = "droneb@ipaddress"
        password = "batman"
        return hostname, password
    if beta == 13: # console
        hostname = "console@ipaddress"
        password = "carnage"
        return hostname, password

# Connects and Runs "killcommand.py" on Drones
def kill_cmd(gamma, delta, epsilon):
    if gamma == "alt":
        command = f'echo {epsilon} | sudo -S python3 ~/Desktop/killcommand.py'  # replace with the correct path to lights.py on the remote host
        ssh_command = f'ssh {delta} "{command}"'
        try:
            child = pexpect.spawn(ssh_command)
            child.expect('password:')
            child.sendline(epsilon)
            child.interact()
        except pexpect.exceptions.ExceptionPexpect as e:
            print(f"SSH connection error: {e}")
        # Turn on Greenlight for 3s
        GPIO.output(4, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(4, GPIO.LOW)
        return
    else:
        return

# Call Function
hostname, password = login_info(tracking)
kill_cmd(status, hostname, password)