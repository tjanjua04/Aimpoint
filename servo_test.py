from gpiozero import AngularServo
from time import sleep

# Initialize the servo with more precise pulse width range for small movements
# Adjust min/max pulse widths for finer control in the -10 to 10 range
servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0024)

while True:
    try:
        # Get user input for the desired angle
        angle = float(input("Enter the angle (-10 to 10): "))
        
        # Ensure the angle is within the valid range for the servo
        if -10 <= angle <= 10:
            # Set the angle
            servo.angle = angle
            print(f"Servo moving to {angle} degrees")
            
            # Sleep for 2 seconds to allow the servo to reach the target position
            sleep(2)
            
            # After the movement, detach the servo to stop sending PWM signals
            servo.angle = None
            print(f"Servo stopped at {angle} degrees")
        else:
            print("Please enter a value between -10 and 10.")
    
    except ValueError:
        print("Invalid input! Please enter a numeric value.")
    
    # Sleep before accepting new input
    sleep(2)
