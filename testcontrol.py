import time
from pyA20.gpio import gpio
from pyA20.gpio import port
from pyA20.i2c import i2c

# Initialize GPIO
gpio.init()

# Configure a GPIO pin for testing
TEST_PIN = port.PA19
gpio.setcfg(TEST_PIN, gpio.OUTPUT)

# Initialize I2C
i2c.init("/dev/i2c-0")
MPU6050_ADDR = 0x68
i2c.open(MPU6050_ADDR)

try:
    # Toggle the GPIO pin
    gpio.output(TEST_PIN, gpio.HIGH)
    time.sleep(1)
    gpio.output(TEST_PIN, gpio.LOW)

    # Read a register from the MPU-6050 to test I2C
    reg = 0x3B  # Example register address
    high = i2c.read_u8(reg)
    low = i2c.read_u8(reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    print("Read value:", value)

except Exception as e:
    print("Error:", e)

finally:
    gpio.output(TEST_PIN, gpio.LOW)
