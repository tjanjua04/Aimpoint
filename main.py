import smbus
import time
import math
from time import sleep
import RPi.GPIO as GPIO

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

# Wake up MPU6050 by writing 0 to register 0x6B
bus.write_byte_data(0x68, 0x6B, 0)

def calculate_aimpoint(putt_dist, avg_y_angle):
    len_outside = .5 * putt_dist * avg_y_angle
    len_outside = abs(len_outside)
    if avg_y_angle <= 0:
        print(f"aim right of center {len_outside:.2f} inches")
    else:
        print(f"aim left of center {len_outside:.2f} inches")
    # Calculate angle in radians
    putt_dist_adj= putt_dist + 2
    angle_radians = math.atan(len_outside / (putt_dist_adj*12))

    # Convert to degrees
    angle_degrees = math.degrees(angle_radians)
        
    return len_outside, angle_degrees


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
    
    x_offset=9.0
    y_offset=0.2
    
    return (avg_x_angle+x_offset), (avg_y_angle-y_offset)

def rotate_servo_to_angle(angle_of_putt, avg_y_angle):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12,GPIO.OUT)
    servo1 = GPIO.PWM(12,50)
    servo1.start(0)
    
    if avg_y_angle >0:
        try:
            #90 is straitght, 100 goes left 10deg, 80 goes right 10 deg
            angle=90+angle_of_putt
            servo1.ChangeDutyCycle(2+(angle/18))
            time.sleep(.5)
            servo1.ChangeDutyCycle(0)
        finally:
            servo1.stop()

    elif avg_y_angle < 0:
        try:
            #90 is straitght, 100 goes left 10deg, 80 goes right 10 deg
            angle=90-angle_of_putt
            servo1.ChangeDutyCycle(2+(angle/18))
            time.sleep(.5)
            servo1.ChangeDutyCycle(0)
        finally:
            servo1.stop()
    else:
        try:
            #90 is straitght, 100 goes left 10deg, 80 goes right 10 deg
            angle=90
            servo1.ChangeDutyCycle(2+(angle/18))
            time.sleep(1)
            servo1.ChangeDutyCycle(0)
        finally:
            servo1.stop()



# Main loop to get input from the user and calculate the average slope
def main():
    while(True):
        GPIO.setmode(GPIO.BOARD)
        # Ask if the user is ready to read the putt
        ready = input("Are you ready to read a putt? (y/n): ").strip().lower()
        
        if ready == 'y':
            # Ask the user for the putt distance        
            putt_dist = float(input("How long is your putt in feet? ").strip())
            print(f"Putt distance: {putt_dist} feet")
            
            # Calculate the average slope (angles)
            avg_x_angle, avg_y_angle = calculate_average_slope()
            
            # Print the average angles (slopes)
            if avg_x_angle == 0:
                print("putt is flat")
            elif avg_x_angle > 0:
                slope= abs(avg_x_angle)
                print (f"\nPutt is up hill by: {slope:.2f}°")
            else:
                slope= abs(avg_x_angle)
                print (f"\nPutt is down hill by: {slope:.2f}°")
            
            if avg_y_angle == 0:
                print("putt is straight")
            elif avg_y_angle > 0:
                LorR = abs(avg_y_angle)
                print(f"Slopes right: {LorR:.2f}°")
            else:
                LorR = abs(avg_y_angle)
                print(f"Slopes left: {LorR:.2f}°")
                
            print("Putt slope calculation complete.")
            #recieve how far out the putt is and the degrees of the putt
            len_outside, angle_of_putt = calculate_aimpoint(putt_dist, avg_y_angle)
            
            #call rotate servo function
            rotate_servo_to_angle(angle_of_putt, avg_y_angle)
            
            #turn on laser for 10 seconds
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(11, GPIO.OUT)  # BOARD pin 11 = BCM 17
            GPIO.output(11, GPIO.HIGH)
            sleep(10)
            GPIO.output(11, GPIO.LOW)
            
            GPIO.cleanup()

            
        else:
            print("Exiting program.")

if __name__ == "__main__":
    main()



