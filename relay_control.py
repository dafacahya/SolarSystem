import time
from pyA20.gpio import gpio
from pyA20.gpio import port

# Konfigurasi pin GPIO untuk relay
RELAY_PIN_1 = port.PB19
RELAY_PIN_2 = port.PB20
RELAY_PIN_3 = port.PB22
RELAY_PIN_4 = port.PB23

# Inisialisasi pin relay sebagai output
gpio.init()
gpio.setcfg(RELAY_PIN_1, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_2, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_3, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_4, gpio.OUTPUT)

def control_relay(predicted_azimuth):
    if predicted_azimuth < 90:
        gpio.output(RELAY_PIN_1, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_1, gpio.LOW)
    elif predicted_azimuth < 180:
        gpio.output(RELAY_PIN_2, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_2, gpio.LOW)
    elif predicted_azimuth < 270:
        gpio.output(RELAY_PIN_3, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_3, gpio.LOW)
    else:
        gpio.output(RELAY_PIN_4, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_4, gpio.LOW)
