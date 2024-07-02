import wiringpi
import time

# Inisialisasi WiringPi dengan menggunakan skema penomoran GPIO
wiringpi.wiringPiSetupGpio()

# Tentukan pin GPIO yang akan digunakan untuk relay (misalnya, GPIO17)
relay_pin = 17

# Set pin relay sebagai output
wiringpi.pinMode(relay_pin, wiringpi.OUTPUT)

try:
    while True:
        # Hidupkan relay (dengan mengatur pin ke LOW)
        wiringpi.digitalWrite(relay_pin, 0)
        print("Relay menyala")
        time.sleep(2)  # Biarkan relay menyala selama 2 detik

        # Matikan relay (dengan mengatur pin ke HIGH)
        wiringpi.digitalWrite(relay_pin, 1)
        print("Relay mati")
        time.sleep(2)  # Biarkan relay mati selama 2 detik

except KeyboardInterrupt:
    print("Program dihentikan")

finally:
    # Bersihkan pengaturan GPIO
    wiringpi.digitalWrite(relay_pin, 1)  # Matikan relay
    print("Relay dimatikan untuk keamanan")
