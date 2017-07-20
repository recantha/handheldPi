import time
from Adafruit_LED_Backpack import AlphaNum4
import socket
import math
import commands
import os
import Adafruit_DHT
from gpiozero import LED, Button, CPUTemperature, PingServer
from wifi import Cell, Scheme
from wireless import Wireless
import requests
import threading
import sqlite3 as sqlite

# Create display instance on default I2C address (0x70) and bus number.
display = AlphaNum4.AlphaNum4()
# Initialize the display. Must be called once before using the display.
display.begin()

blue_led = LED(24)
button = Button(11)
low_battery = Button(10)

message_speed = 0.2
ping_delay = 3

hosts_to_monitor = [
    ['WWW', 'www.thecasecentre.org','case method'],
    ['ADMIN', 'admin.thecasecentre.org', 'admin site'],
    ['RECANTHA', 'recantha.co.uk', 'Raspberry Pi Pod']
]

wireless = Wireless()

# Scroll a message across the display
def show_message(message, current_operation):
    global operation

    pos = 0

    print(message)

    while pos < len(message) and operation == current_operation:
        display.clear()
        display.print_str(message[pos:pos+4])
        display.write_display()
        pos += 1

        time.sleep(message_speed)

    display.clear()

def readIPaddresses():
    ips = commands.getoutput("/sbin/ifconfig | grep -i \"inet\" | grep -iv \"inet6\" | " + "awk {'print $2'} | sed -ne 's/addr\:/ /p'")
    addrs = ips.split('\n')

    return addrs

def shutdown():
    print("Shutdown requested")
    show_message("Shutdown", 0)
    display.clear()
    blue_led.off()
    os.system("sudo halt")

def getCPUtemperature():
    cpu = CPUTemperature()
    temp_C = int(float(cpu.temperature))
    temp_F = round(9.0/5.0*temp_C+32)
    temp_C = round(temp_C)

    return temp_C, temp_F

def increaseOperation():
    global operation
    operation += 1

def scanForCells():
    cells = Cell.all('wlan0')

    for cell in cells:
        cell.summary = 'SSID {} / Qual {}'.format(cell.ssid, cell.quality)

        if cell.encrypted:
            enc_yes_no = '*'
        else:
            enc_yes_no = '()'

        cell.summary = cell.summary + ' / Enc {}'.format(enc_yes_no)

    return cells

class readingsThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    
    def run(self):
        try:
            con = sqlite.connect('handheldPi.db')
            while True:
                cur = con.cursor()
                humidity, temperature = Adafruit_DHT.read_retry(11, 23)
                cur.execute("INSERT INTO readings (reading_date, reading_time, reading_type, value) VALUES (date('now'), time('now'), 'temperature', ?)", (temperature,))
                con.commit()
                time.sleep(5)

        except sqlite.Error, e:
            if con:
                con.rollback()

            print("Error %s:" % e.args[0])
            con.close()
            sys.exit()

thread1 = readingsThread(1, "readings")
thread1.start()

# Start conditions
# Turn the blue LED on
blue_led.on()
# When button is pressed, move to next operation
button.when_pressed = increaseOperation
# When button is held for 5 seconds, trigger the shutdown
button.hold_time = 5
button.when_held = shutdown
# When low battery alert goes high, trigger the shutdown
low_battery.when_pressed = shutdown

operation = 0

try:
    while True:
        blue_led.on()

        if operation == 0:
            hostname = socket.gethostname()
            show_message(hostname, operation)

        elif operation == 1:
            current_ap = wireless.current()
            show_message("Connected to %s" % current_ap, operation)

        elif operation == 2:
            ip_addresses = readIPaddresses()

            for addr in ip_addresses:
                if operation == 2:
                    show_message(addr, operation)

        elif operation == 3:
            # DHT11 on pin 23
            humidity, temperature = Adafruit_DHT.read_retry(11, 23)
            show_message('Temp {0:0.1f}C  Humid {1:0.1f}%'.format(temperature, humidity), operation)

        elif operation == 4:
            temp_C, temp_F = getCPUtemperature()
            show_message("CPU {}C / {}F".format(temp_C, temp_F), operation)

        elif operation == 5:
            show_message('Wifi Networks', operation)
            cells = scanForCells()
            for cell in cells:
                if operation == 5:
                    show_message(cell.summary, operation)

        elif operation == 6:
            blue_led.off()
            for host in hosts_to_monitor:
                if operation == 6:
                    nickname, server, match = host
                    pinger = PingServer(server)
                    if pinger.value:
                        status = "UP"
                        blue_led.off()
                    else:
                        status = "DOWN"
                        blue_led.blink()

                    show_message("Ping to {} - {}".format(server, status), operation)

                    for i in range(0,ping_delay):
                        if operation == 6:
                            time.sleep(1)

        elif operation == 7:
            blue_led.off()
            for host in hosts_to_monitor:
                if operation == 7:
                    nickname, server, match = host

                    show_message("Ping {}".format(nickname), operation)

                    pinger = PingServer(server)

                    if not pinger.value:
                        status = "DOWN"
                        emoji = ":-("
                        blue_led.blink()

                    else:
                        show_message("Scrape {}".format(nickname), operation)

                        response = requests.get('http://{}'.format(server))
                        page = response.text
                        if page.find(match) > -1:
                            status = "OK"
                            emoji = ":-)"
                            blue_led.off()
                        else:
                            status = "DOWN"
                            blue_led.blink()
                            emoji = ":-("

                    show_message("Status {} - {}".format(nickname, status), operation)

                    for i in range(0, ping_delay):
                        if operation == 7:
                            time.sleep(1)

        else:
            operation = 0

except:
    print("Exiting")
    thread1.join()
    sys.exit()
