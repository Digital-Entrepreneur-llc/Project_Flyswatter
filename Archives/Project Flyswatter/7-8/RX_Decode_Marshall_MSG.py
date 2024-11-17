import socket
import binascii
import struct
import time

# Define the UDP socket settings
UDP_IP = "192.168.1.1"
UDP_PORT = 45000

# Initialize the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

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
        print(f"Error decoding message: {e}")
        return None

if __name__ == "__main__":
    print("UDP server is listening for Marshall messages...")
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f"Received message from {addr}")
        decoded_message = decode_marshall_message(data)
        if decoded_message:
            print("Decoded Marshall Message:")
            for key, value in decoded_message.items():
                print(f"{key}: {value}")
