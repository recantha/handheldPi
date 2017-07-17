# handheldPi
Code for a handheld device with various functions.

![Picture of device](https://github.com/recantha/handheldPi/raw/master/handheldPi.jpg "Picture of the handheldPi device")

# Functions of the handheldPi
* Displays current hostname
* Displays currently connected-to wifi access point
* Displays all the current IP addresses
* Displays temperature and humidity from attached DHT11 sensor
* Displays current CPU temperature in Celsius and Fahrenheit
* Scans for and displays all local wifi networks, their signal quality and whether they're encrypted or not
* Pings two servers to see if they are up and displays their status - Up/Down indicator 1
* Web-scrapes the same two servers to see if matching text is found - Up/Down indicator 2

# Libraries to install
* GPIO Zero (comes with Raspbian)
* https://github.com/adafruit/Adafruit_LED_Backpack
* https://github.com/adafruit/Adafruit_Python_DHT
* sudo pip install wireless
* sudo pip install wifi
* sudo pip install requests

