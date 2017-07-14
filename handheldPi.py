import time
from Adafruit_LED_Backpack import AlphaNum4
import socket
import math
import commands
import os
import Adafruit_DHT
from wireless import Wireless

from gpiozero import LED, Button

# Create display instance on default I2C address (0x70) and bus number.
display = AlphaNum4.AlphaNum4()
# Initialize the display. Must be called once before using the display.
display.begin()

blue_led = LED(24)
button = Button(11)
low_battery = Button(10)

wireless = Wireless()

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

def getCPUtemperature():
    res = os.popen("vcgencmd measure_temp").readline()
    temp_C = res.replace("temp=","").replace("'C\n", "")
    temp_C = int(float(temp_C))
    temp_F = round(9.0/5.0*temp_C+32)
    temp_C = round(temp_C)

    return temp_C, temp_F

def increaseOperation():
    global operation
    operation += 1

# Start conditions
operation = 0

blue_led.on()
hold_time = 5
button.when_pressed = increaseOperation
button.when_held = shutdown
low_battery.when_pressed = shutdown

while True:
    if operation == 0:
        hostname = socket.gethostname()
        show_message(hostname)

    elif operation == 1:
        current_ap = wireless.current()
        show_message("Connected to %s" % current_ap)

    elif operation == 2:
        ip_addresses = readIPaddresses()

        for addr in ip_addresses:
            show_message(addr)

    elif operation == 3:
        # DHT11 on pin 23
        humidity, temperature = Adafruit_DHT.read_retry(11, 23)
        show_message('Temp {0:0.1f}C  Humid {1:0.1f}%'.format(temperature, humidity))

    elif operation == 4:
        temp_C, temp_F = getCPUtemperature()
        show_message("CPU {}C / {}F".format(temp_C, temp_F))

    else:
        operation = 0
