# GPIO Setup & Module Import
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(1, GPIO.OUT)

# Turn on Cue for 10s
GPIO.output(1, GPIO.HIGH)
time.sleep(10)
GPIO.output(1, GPIO.LOW)
print("done")