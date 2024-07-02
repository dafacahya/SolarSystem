import OrangePi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering scheme

# Define GPIO pins
RELAY_PIN = 12  # Example pin

# Setup GPIO pin
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    while True:
        # Turn on the actuator
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("Actuator ON")
        time.sleep(2)

        # Turn off the actuator
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Actuator OFF")
        time.sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()
