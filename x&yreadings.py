import smbus
import time
import math

# MPU6050 I2C address
MPU6050_ADDR = 0x68

# MPU6050 registers for accelerometer data
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40

# Initialize I2C (SMBus)
bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi

# Wake up the MPU6050 (default power-up state is sleep mode)
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)

# Function to read 2 bytes (16-bit value) from the sensor
def read_word(reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value -= 0x10000  # Convert to signed 16-bit value
    return value

# Function to get accelerometer data (X, Y, Z)
def get_accel_data():
    ax = read_word(ACCEL_XOUT_H)
    ay = read_word(ACCEL_YOUT_H)
    az = read_word(ACCEL_ZOUT_H)
    return ax, ay, az

# Function to calculate the angle of the X-axis in degrees
def calculate_x_axis_angle(ax, az):
    # Calculate the angle (in degrees) based on the X and Z accelerometer data
    angle = math.atan2(ax, az) * 180 / math.pi
    return angle

# Function to calculate the angle of the Y-axis in degrees
def calculate_y_axis_angle(ay, az):
    # Calculate the angle (in degrees) based on the Y and Z accelerometer data
    angle = math.atan2(ay, az) * 180 / math.pi
    return angle

# Function to calculate the average angles once
def calculate_average_slope():
    # Collect data for 5 seconds
    print("Calculating slope...")
    start_time = time.time()
    x_angles = []
    y_angles = []
    
    # Collect data for 5 seconds
    while time.time() - start_time < 5:
        ax, ay, az = get_accel_data()
        
        # Calculate angles for X and Y axes
        x_angle = calculate_x_axis_angle(ax, az)
        y_angle = calculate_y_axis_angle(ay, az)
        
        # Append the angles to their respective lists
        x_angles.append(x_angle)
        y_angles.append(y_angle)
        
        time.sleep(0.1)  # Sampling interval
    
    # Calculate the average angles
    avg_x_angle = sum(x_angles) / len(x_angles)
    avg_y_angle = sum(y_angles) / len(y_angles)
    
    return avg_x_angle, avg_y_angle

# Main loop to get input from the user and calculate the average slope
def main():
    # Ask if the user is ready to read the putt
    ready = input("Are you ready to read a putt? (y/n): ").strip().lower()
    
    if ready == 'y':
        # Ask the user for the putt distance
        putt_dist = input("How long is your putt in feet? ").strip()
        print(f"Putt distance: {putt_dist} feet")
        
        # Calculate the average slope (angles)
        avg_x_angle, avg_y_angle = calculate_average_slope()
        
        # Print the average angles (slopes)
        print(f"\nAverage up/down slope is: {avg_x_angle:.2f}°")
        print(f"\033[32mAverage left to right slope is (negative slopes left): {avg_y_angle:.2f}°\033[0m")  # Green color for Y-axis
        
        print("Putt slope calculation complete.")
    
    else:
        print("Exiting program.")

if __name__ == "__main__":
    main()

