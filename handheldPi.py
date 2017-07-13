import time
from Adafruit_LED_Backpack import AlphaNum4
import socket
import math
import commands
import os

from gpiozero import LED, Button

# Create display instance on default I2C address (0x70) and bus number.
display = AlphaNum4.AlphaNum4()
# Initialize the display. Must be called once before using the display.
display.begin()

blue_led = LED(24)
shutdown_button = Button(11)
low_battery = Button(10)

# Scroll a message across the display
def show_message(message):
    pos = 0

    print(message)

    while pos < len(message):
        display.clear()
        display.print_str(message[pos:pos+4])
        display.write_display()
        pos += 1

        time.sleep(0.3)

    display.clear()

def readIPaddresses():
    ips = commands.getoutput("/sbin/ifconfig | grep -i \"inet\" | grep -iv \"inet6\" | " + "awk {'print $2'} | sed -ne 's/addr\:/ /p'")
    addrs = ips.split('\n')

    return addrs

def shutdown():
    print("Shutdown requested")
    show_message("Shutdown")
    display.clear()
    blue_led.off()
    os.system("sudo halt")

operation = 0

blue_led.on()
shutdown_button.when_pressed = shutdown
low_battery.when_pressed = shutdown

while True:
    if operation == 0:
        hostname = socket.gethostname()
        show_message(hostname)
        operation = 1

    elif operation == 1:
        ip_addresses = readIPaddresses()

        for addr in ip_addresses:
            show_message(addr)

        operation = 0

