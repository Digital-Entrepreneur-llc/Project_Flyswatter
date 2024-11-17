import math
import serial
import time
import tkinter as tk
from configparser import ConfigParser

# Function to read configuration settings
def read_config(file='config.ini'):
    config = ConfigParser()
    config.read(file)
    settings = config['Settings']
    known_point = (float(settings['known_latitude']), float(settings['known_longitude']))
    heading = float(settings['heading'])
    left_boundary = float(settings['left_boundary'])
    right_boundary = float(settings['right_boundary'])
    return known_point, heading, left_boundary, right_boundary

# Function to convert NMEA latitude/longitude to decimal degrees
def nmea_to_decimal(degrees, minutes, direction):
    try:
        decimal = float(degrees) + float(minutes) / 60.0
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except ValueError as e:
        print(f"ValueError in nmea_to_decimal: {e}")
        return None

# Function to calculate the distance between two points using Haversine formula
def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371e3  # Radius of Earth in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Function to calculate the bearing between two points
def calculate_bearing(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    
    delta_lon = lon2 - lon1
    
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

# Function to determine if the current point is within the defined area
def is_within_area(current_point, known_point, heading, left_boundary, right_boundary, max_distance=800):
    distance = haversine_distance(current_point, known_point)
    print(f"Distance: {distance} meters")
    
    if distance > max_distance:
        print(f"Outside maximum distance: {distance} > {max_distance}")
        return False

    bearing = calculate_bearing(known_point, current_point)
    print(f"Bearing: {bearing} degrees")

    left_angle = (heading + left_boundary) % 360
    right_angle = (heading + right_boundary) % 360

    print(f"Left Angle: {left_angle} degrees, Right Angle: {right_angle} degrees")

    if left_angle < right_angle:
        within_boundaries = left_angle <= bearing <= right_angle
    else:
        within_boundaries = bearing >= left_angle or bearing <= right_angle

    print(f"Within Boundaries: {within_boundaries}")

    return within_boundaries

# Function to display a popup message
def show_popup(title, message, color, fire_now=False, current_point=None):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    popup = tk.Toplevel(root)
    popup.title(title)

    label = tk.Label(popup, text=message, font=("Helvetica", 16), fg=color)
    label.pack(pady=10)

    if fire_now:
        fire_label = tk.Label(popup, text="FIRE NOW!!", font=("Helvetica", 24, "bold"), fg="red")
        fire_label.pack(pady=5)

        # Make the "FIRE NOW!!" text flash
        def flash():
            current_color = fire_label.cget("foreground")
            next_color = "red" if current_color == "black" else "black"
            fire_label.config(foreground=next_color)
            popup.after(500, flash)  # Flash every 500ms

        flash()

    if current_point:
        coords_label = tk.Label(popup, text=f"Detected Coordinates: {current_point[0]}, {current_point[1]}", font=("Helvetica", 12))
        coords_label.pack(pady=5)

    root.mainloop()

# Function to read from serial port and check if the GPS point is within the defined area
def read_serial_data():
    known_point, heading, left_boundary, right_boundary = read_config()

    try:
        ser = serial.Serial('/dev/ttyUSB4', 9600, timeout=1)
        time.sleep(2)  # Wait for the connection to initialize

        print("Connected to serial port")

        while True:
            try:
                line = ser.readline().decode('ascii', errors='replace').strip()
                print(f"Received: {line}")

                if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                    data = line.split(',')
                    if len(data) > 5 and data[2] and data[4]:  # Check for valid data
                        try:
                            lat_deg = data[2][:2]
                            lat_min = data[2][2:]
                            lon_deg = data[4][:3]
                            lon_min = data[4][3:]

                            if not (lat_deg.isdigit() and lon_deg.isdigit() and lat_min.replace('.', '', 1).isdigit() and lon_min.replace('.', '', 1).isdigit()):
                                print("Invalid latitude or longitude data")
                                continue

                            lat = nmea_to_decimal(lat_deg, lat_min, data[3])
                            lon = nmea_to_decimal(lon_deg, lon_min, data[5])
                            if lat is None or lon is None:
                                print("Invalid latitude or longitude conversion")
                                continue

                            current_point = (lat, lon)
                            print(f"Parsed GPS coordinates: {current_point}")

                            if is_within_area(current_point, known_point, heading, left_boundary, right_boundary):
                                show_popup("Alert", "UAS DETECTED WITHIN FLYSWATTER!!!", "red", fire_now=True, current_point=current_point)
                            else:
                                show_popup("Status", "Airspace is Clear", "green")
                        except ValueError as e:
                            print(f"ValueError while parsing NMEA data: {e}")
                            continue
                    else:
                        print("Invalid data length or missing data in NMEA string")

                time.sleep(1)

            except serial.SerialException as e:
                print(f"SerialException during read: {e}")
                break  # Exit the loop and try to reconnect

            except Exception as e:
                print(f"Error during read: {e}")

    except serial.SerialException as e:
        print(f"SerialException during connection: {e}")

    except Exception as e:
        print(f"Error during connection: {e}")

    finally:
        try:
            ser.close()
        except:
            pass

# Start serial reading
read_serial_data()

