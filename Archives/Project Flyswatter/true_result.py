import tkinter as tk
import math
from geopy.distance import geodesic

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

# Function to display a pop-up window
def show_popup(title, message, color, fire_now=False):
    root = tk.Tk()
    root.title(title)
    
    label = tk.Label(root, text=message, fg=color, font=("Helvetica", 16))
    label.pack(pady=10)
    
    if fire_now:
        fire_label = tk.Label(root, text="FIRE NOW!!", fg="red", font=("Helvetica", 16, "bold"))
        fire_label.pack(pady=10)
        # Create a flashing effect
        def flash():
            current_color = fire_label.cget("foreground")
            next_color = "red" if current_color == "white" else "white"
            fire_label.config(foreground=next_color)
            root.after(500, flash)
        flash()
    
    root.mainloop()

# Hard-coded test data
known_point = (47.09, -122.55)
current_point = (47.091, -122.549)  # Adjusted to be within the area
heading = 10.0
left_boundary = 265.0
right_boundary = 45.0

if is_within_area(current_point, known_point, heading, left_boundary, right_boundary):
    show_popup("Alert", "UAS DETECTED WITHIN FLYSWATTER!!!", "red", fire_now=True)
else:
    show_popup("Status", "Airspace is Clear", "green")
