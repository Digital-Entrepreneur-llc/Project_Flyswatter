import configparser
import serial
import time
import math
from geopy.distance import geodesic
import paramiko

# Function to convert NMEA latitude and longitude to decimal degrees
def nmea_to_decimal(degrees, minutes, direction):
    decimal = float(degrees) + float(minutes) / 60
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

# Function to calculate the bearing between two points
def calculate_bearing(pointA, pointB):
    lat1, lon1 = math.radians(pointA[0]), math.radians(pointA[1])
    lat2, lon2 = math.radians(pointB[0]), math.radians(pointB[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

# Function to check if the GPS point is within the defined area
def is_within_area(current_point, known_point, heading, left_boundary, right_boundary):
    max_distance = 800.0  # Hard-coded maximum distance in meters
    distance = geodesic(known_point, current_point).meters
    if distance > max_distance:
        return False

    bearing = calculate_bearing(known_point, current_point)
    left_angle = (heading - left_boundary + 360) % 360
    right_angle = (heading + right_boundary + 360) % 360

    if left_angle < right_angle:
        return left_angle <= bearing <= right_angle
    else:
        return bearing >= left_angle or bearing <= right_angle

# Function to run a command on a remote machine over SSH
def run_ssh_command(host, port, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())
    ssh.close()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

known_lat = float(config['Settings']['known_latitude'])
known_lon = float(config['Settings']['known_longitude'])
known_point = (known_lat, known_lon)
heading = float(config['Settings']['heading'])
left_boundary = float(config['Settings']['left_boundary'])
right_boundary = float(config['Settings']['right_boundary'])

# SSH details
ssh_host = "192.168.1.110"
ssh_port = 22
ssh_username = "engagementstation"
ssh_password = "letmein"
ssh_command = "python3 light.py"

# Initialize serial connection
ser = serial.Serial('COM3', 4800, timeout=1)  # Change COM3 to your COM port
time.sleep(2)  # Wait for the connection to initialize

try:
    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        if line.startswith('$GPGGA'):
            data = line.split(',')
            if len(data) > 5 and data[2] and data[4]:  # Check for valid data
                lat = nmea_to_decimal(data[2][:2], data[2][2:], data[3])
                lon = nmea_to_decimal(data[4][:3], data[4][3:], data[5])
                current_point = (lat, lon)

                if is_within_area(current_point, known_point, heading, left_boundary, right_boundary):
                    print(f"Position within area: {current_point}")
                    run_ssh_command(ssh_host, ssh_port, ssh_username, ssh_password, ssh_command)
                else:
                    print(f"Position outside area: {current_point}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    ser.close()