import serial
import time
import binascii
import math
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the UDP socket settings
UDP_Source_IP = "192.168.0.199"
UDP_Destination_IP1 = "239.255.255.254"  # Multicast
UDP_Source_PORT = 45000
UDP_Destination_PORT1 = 45000
UDP_Destination_IP2 = "239.255.255.253"  # Another Multicast address
UDP_Destination_PORT2 = 45001

# Initialize the UDP sockets
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP for destination 1
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP for destination 2

# Bind the source IP and port for receiving data
sock1.bind((UDP_Source_IP, UDP_Source_PORT))

def read_serial_data():
    while True:
        ser = None
        try:
            # Open serial port with the correct settings
            ser = serial.Serial(
                port='/dev/ttyS0',    # Use /dev/ttyS0 as your serial port
                baudrate=9600,        # Set the baudrate
                timeout=1             # Read timeout in seconds
            )

            # Check if the serial port is open
            if ser.is_open:
                logging.info("Serial port opened successfully")
                while True:
                    try:
                        # Read data from the serial port
                        if ser.in_waiting > 0:
                            data = ser.readline().decode('utf-8').rstrip()
                            logging.debug(f"Received: {data}")
                            if "GGA" in data:
                                marshall_message = convert_NMEA_to_Marshall(data)
                                if marshall_message != -1:
                                    logging.debug(f"Marshall Message: {binascii.hexlify(marshall_message)}")
                                    # Send the Marshall message to both UDP destinations
                                    sock1.sendto(marshall_message, (UDP_Destination_IP1, UDP_Destination_PORT1))
                                    sock2.sendto(marshall_message, (UDP_Destination_IP2, UDP_Destination_PORT2))
                    except serial.SerialException as e:
                        logging.error(f"Read error: {e}")
                        break  # Exit the inner loop to attempt reopening the port
                    except OSError as e:
                        logging.error(f"OS error during read: {e}")
                        break  # Exit the inner loop to attempt reopening the port

        except serial.SerialException as e:
            logging.error(f"Connection error: {e}")
        except OSError as e:
            logging.error(f"OS error during connection: {e}")

        finally:
            # Close the serial port
            if ser and ser.is_open:
                ser.close()
                logging.info("Serial port closed")

        # Wait before attempting to reconnect
        time.sleep(5)

def convert_NMEA_to_Marshall(GGA_NMEA_String, Tail_Number=1):
    # Parsing the GGA NMEA message
    GGA_NMEA_Split = GGA_NMEA_String.split(",")

    # Validate message is GGA
    if "GGA" not in GGA_NMEA_Split[0]:
        logging.warning("Data not GGA")
        return -1

    try:
        # Grab necessary data
        # Latitude
        NMEA_Latitude = GGA_NMEA_Split[2]
        # Format is in DDMM.MMMMM
        # Pull Degrees
        NMEA_Latitude_Degrees = int(NMEA_Latitude[0:2])
        # Pull Minutes and convert to degrees
        NMEA_Latitude_Degrees_Decimal = float(NMEA_Latitude[2:]) / 60
        # Pull sign
        NMEA_Latitude_Sign = 1 if GGA_NMEA_Split[3] == "N" else -1
        # Combine
        NMEA_Latitude = NMEA_Latitude_Sign * (NMEA_Latitude_Degrees + NMEA_Latitude_Degrees_Decimal)

        # Longitude
        NMEA_Longitude = GGA_NMEA_Split[4]
        # Format is in DDDMM.MMMMM
        # Pull Degrees
        NMEA_Longitude_Degrees = int(NMEA_Longitude[0:3])
        # Pull Minutes and convert to degrees
        NMEA_Longitude_Degrees_Decimal = float(NMEA_Longitude[3:]) / 60
        # Pull sign
        NMEA_Longitude_Sign = 1 if GGA_NMEA_Split[5] == "E" else -1
        # Combine
        NMEA_Longitude = NMEA_Longitude_Sign * (NMEA_Longitude_Degrees + NMEA_Longitude_Degrees_Decimal)

        # Altitude
        NMEA_Altitude = float(GGA_NMEA_Split[9])

        # Build up Marshall Message
        UAS_LSUL = '060e2b34020b01010e01030101000000'
        Payload_Length = '39'
        Precision_Time_Stamp_Tag_Number = '02'
        Precision_Time_Stamp_Tag_Length = '08'
        Precision_Time_Stamp_Tag_Value = int(time.time() * 1000000)
        Precision_Time_Stamp_Tag_Value = binascii.hexlify(Precision_Time_Stamp_Tag_Value.to_bytes(8, byteorder="big")).decode()

        Sensor_Latitude_Tag_Number = '0D'
        Sensor_Latitude_Tag_Length = '04'
        Sensor_Latitude_Tag_Value = int(NMEA_Latitude * ((2**32 - 2) / 180))
        Sensor_Latitude_Tag_Value = binascii.hexlify(Sensor_Latitude_Tag_Value.to_bytes(4, byteorder="big", signed=True)).decode()

        Sensor_Longitude_Tag_Number = '0E'
        Sensor_Longitude_Tag_Length = '04'
        Sensor_Longitude_Tag_Value = int(NMEA_Longitude * ((2**32 - 2) / 360))
        Sensor_Longitude_Tag_Value = binascii.hexlify(Sensor_Longitude_Tag_Value.to_bytes(4, byteorder="big", signed=True)).decode()

        Sensor_Ellipsoid_Height_Tag_Number = '4B'
        Sensor_Ellipsoid_Height_Tag_Length = '02'
        Sensor_Ellipsoid_Height_Tag_Value = int(((2**16 - 1) / 19900) * (NMEA_Altitude + 900))
        Sensor_Ellipsoid_Height_Tag_Value = binascii.hexlify(Sensor_Ellipsoid_Height_Tag_Value.to_bytes(2, byteorder="big", signed=True)).decode()

        Range_Image_Local_Set_Tag_Number = '61'
        Range_Image_Local_Set_Tag_Length = '01'
        Range_Image_Local_Set_Tag_Value = binascii.hexlify((0).to_bytes(1, byteorder="big")).decode()

        Platform_Tail_Number_Tag_Number = '04'
        Platform_Tail_Number_Tag_Length = '09'
        Platform_Tail_Number_Tag_Value = ("BIRD_" + str(Tail_Number).rjust(3, "0")).encode("utf-8").hex().ljust(18, "0")

        Mission_ID_Tag_Number = '03'
        Mission_ID_Tag_Length = '0B'
        Mission_ID_Tag_Value = "1-51 Test".encode("utf-8").hex().ljust(22, "0")

        Checksum_Tag_Number = '01'
        Checksum_Tag_Length = '02'
        Checksum_Tag_Value = binascii.hexlify((0).to_bytes(2, byteorder="big", signed=True)).decode()

        Header = UAS_LSUL + Payload_Length
        Time_Stamp_Tag = Precision_Time_Stamp_Tag_Number + Precision_Time_Stamp_Tag_Length + Precision_Time_Stamp_Tag_Value
        Sensor_Latitude_Tag = Sensor_Latitude_Tag_Number + Sensor_Latitude_Tag_Length + Sensor_Latitude_Tag_Value
        Sensor_Longitude_Tag = Sensor_Longitude_Tag_Number + Sensor_Longitude_Tag_Length + Sensor_Longitude_Tag_Value
        Sensor_Ellipsoid_Height_Tag = Sensor_Ellipsoid_Height_Tag_Number + Sensor_Ellipsoid_Height_Tag_Length + Sensor_Ellipsoid_Height_Tag_Value
        Range_Image_Local_Set_Tag = Range_Image_Local_Set_Tag_Number + Range_Image_Local_Set_Tag_Length + Range_Image_Local_Set_Tag_Value
        Platform_Tail_Number_Tag = Platform_Tail_Number_Tag_Number + Platform_Tail_Number_Tag_Length + Platform_Tail_Number_Tag_Value
        Mission_ID_Tag = Mission_ID_Tag_Number + Mission_ID_Tag_Length + Mission_ID_Tag_Value
        Checksum_Tag = Checksum_Tag_Number + Checksum_Tag_Length + Checksum_Tag_Value

        Marshall_Message = Header + Time_Stamp_Tag + Sensor_Latitude_Tag + Sensor_Longitude_Tag + Sensor_Ellipsoid_Height_Tag + Range_Image_Local_Set_Tag + Platform_Tail_Number_Tag + Mission_ID_Tag + Checksum_Tag
        Marshall_Message = binascii.unhexlify(Marshall_Message)

        return Marshall_Message

    except (ValueError, IndexError) as e:
        logging.error(f"Data parsing error: {e}")
        return -1

if __name__ == "__main__":
    try:
        read_serial_data()
    finally:
        # Close the UDP sockets when done
        sock1.close()
        sock2.close()