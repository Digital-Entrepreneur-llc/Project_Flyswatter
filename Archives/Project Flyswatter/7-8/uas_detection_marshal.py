import math
import socket
import tkinter as tk
from configparser import ConfigParser
import binascii
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read configuration settings
def read_config(file='config.ini'):
    config = ConfigParser()
    config.read(file)
    settings = config['Settings']
    known_point = (float(settings['known_latitude']), float(settings['known_longitude']))
    heading = float(settings['heading'])
    left_boundary = float(settings['left_boundary'])
    right_boundary = float(settings['right_boundary'])
    min_altitude = float(settings['min_altitude'])
    max_altitude = float(settings['max_altitude'])
    return known_point, heading, left_boundary, right_boundary, min_altitude, max_altitude

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

# Function to determine if a point is within a defined area based on bearing and boundaries
def is_within_area(current_point, known_point, heading, left_boundary, right_boundary, min_altitude, max_altitude, altitude):
    distance = haversine_distance(known_point, current_point)
    bearing = calculate_bearing(known_point, current_point)
    
    relative_bearing = (bearing - heading + 360) % 360

    return (left_boundary <= relative_bearing <= right_boundary) and (min_altitude <= altitude <= max_altitude)

# Function to show popup alert
def show_popup(title, message, color, fire_now=False, current_point=None):
    popup = tk.Tk()
    popup.wm_title(title)
    label = tk.Label(popup, text=message, font=("Helvetica", 16), fg=color)
    label.pack(side="top", fill="x", pady=10)
    if current_point:
        details = f"Latitude: {current_point[0]:.6f}, Longitude: {current_point[1]:.6f}, Altitude: {current_point[2]:.2f}m"
        detail_label = tk.Label(popup, text=details, font=("Helvetica", 10))
        detail_label.pack(side="top", fill="x", pady=5)
    B1 = tk.Button(popup, text="OK", command=popup.destroy)
    B1.pack()
    if fire_now:
        # Add code to handle the fire now logic if necessary
        pass
    popup.mainloop()

# Function to decode Marshall message
def decode_marshall_message(data):
    try:
        # Convert the binary data to hex string
        hex_data = binascii.hexlify(data).decode()

        # Extract each component based on the known structure of the Marshall message
        UAS_LSUL = hex_data[0:32]
        Payload_Length = hex_data[32:34]

        Precision_Time_Stamp_Tag_Number = hex_data[34:36]
        Precision_Time_Stamp_Tag_Length = hex_data[36:38]
        Precision_Time_Stamp_Tag_Value = hex_data[38:54]
        Precision_Time_Stamp_Tag_Value = int(Precision_Time_Stamp_Tag_Value, 16) / 1000000.0

        Sensor_Latitude_Tag_Number = hex_data[54:56]
        Sensor_Latitude_Tag_Length = hex_data[56:58]
        Sensor_Latitude_Tag_Value = hex_data[58:66]
        Sensor_Latitude = int(Sensor_Latitude_Tag_Value, 16) * 180 / (2**32 - 2)

        Sensor_Longitude_Tag_Number = hex_data[66:68]
        Sensor_Longitude_Tag_Length = hex_data[68:70]
        Sensor_Longitude_Tag_Value = hex_data[70:78]
        Sensor_Longitude = int(Sensor_Longitude_Tag_Value, 16) * 360 / (2**32 - 2)

        Sensor_Ellipsoid_Height_Tag_Number = hex_data[78:80]
        Sensor_Ellipsoid_Height_Tag_Length = hex_data[80:82]
        Sensor_Ellipsoid_Height_Tag_Value = hex_data[82:86]
        Sensor_Ellipsoid_Height = int(Sensor_Ellipsoid_Height_Tag_Value, 16) * 19900 / (2**16 - 1) - 900

        Range_Image_Local_Set_Tag_Number = hex_data[86:88]
        Range_Image_Local_Set_Tag_Length = hex_data[88:90]
        Range_Image_Local_Set_Tag_Value = hex_data[90:92]

        Platform_Tail_Number_Tag_Number = hex_data[92:94]
        Platform_Tail_Number_Tag_Length = hex_data[94:96]
        Platform_Tail_Number_Tag_Value = hex_data[96:114]
        Platform_Tail_Number = binascii.unhexlify(Platform_Tail_Number_Tag_Value).decode().rstrip('\x00')

        Mission_ID_Tag_Number = hex_data[114:116]
        Mission_ID_Tag_Length = hex_data[116:118]
        Mission_ID_Tag_Value = hex_data[118:140]
        Mission_ID = binascii.unhexlify(Mission_ID_Tag_Value).decode().rstrip('\x00')

        Checksum_Tag_Number = hex_data[140:142]
        Checksum_Tag_Length = hex_data[142:144]
        Checksum_Tag_Value = hex_data[144:148]

        decoded_message = {
            "UAS_LSUL": UAS_LSUL,
            "Payload_Length": Payload_Length,
            "Precision_Time_Stamp": Precision_Time_Stamp_Tag_Value,
            "Sensor_Latitude": Sensor_Latitude,
            "Sensor_Longitude": Sensor_Longitude,
            "Sensor_Ellipsoid_Height": Sensor_Ellipsoid_Height,
            "Range_Image_Local_Set": Range_Image_Local_Set_Tag_Value,
            "Platform_Tail_Number": Platform_Tail_Number,
            "Mission_ID": Mission_ID,
            "Checksum": Checksum_Tag_Value
        }

        return decoded_message

    except Exception as e:
        logging.error(f"Error decoding message: {e}")
        return None

if __name__ == "__main__":
    known_point, heading, left_boundary, right_boundary, min_altitude, max_altitude = read_config()

    print("UDP server is listening for Marshall messages...")
    UDP_IP = "192.168.1.1"
    UDP_PORT = 45000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f"Received message from {addr}")
        decoded_message = decode_marshall_message(data)
        if decoded_message:
            print("Decoded Marshall Message:")
            for key, value in decoded_message.items():
                print(f"{key}: {value}")

            latitude = decoded_message["Sensor_Latitude"]
            longitude = decoded_message["Sensor_Longitude"]
            altitude = decoded_message["Sensor_Ellipsoid_Height"]

            current_point = (latitude, longitude, altitude)

            if is_within_area(current_point, known_point, heading, left_boundary, right_boundary, min_altitude, max_altitude, altitude):
                show_popup("Alert", "UAS DETECTED WITHIN FLYSWATTER!!!", "red", fire_now=True, current_point=current_point)
            else:
                show_popup("Status", "Airspace is Clear", "green")
