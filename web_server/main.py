import network
import socket
import time
from micropython import const
from machine import Pin, I2C
import uasyncio as asyncio
import ntptime

from wlanc import ssid, password

## set up OLED Display ##
OLED_WIDTH = const(128)
OLED_HEIGHT = const(32)

import ssd1306

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

## set up BME280 ##
WAIT_READING = const(60) # Wait one minute before new sensor reading
WAIT_MAIN    = const(60) # Wait one minute in main loop

import bme280_float as bme280

# Assume OLED and BME280 will share the same i2c pins
bme = bme280.BME280(i2c=i2c)
print(bme.values)

# global variable
reading = "BME280 Sensor"

## set up onboard LED ##
led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)

# Refresh every 60 seconds
def webpage():
    global reading
    lt = time.localtime()
    t = f'{lt[2]:02}/{lt[1]:02}/{lt[0]} {lt[3]:02}:{lt[4]:02}'
    page = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Pico W BME280 Weather Station</title>
            <meta http-equiv="refresh" content="60">
            <link rel="icon" href="data:," />
            </head>
            <body>
            <p>{t}</p>
            <p>{reading}</p>
            </body>
            </html>
            """
    return page

wlan = network.WLAN(network.STA_IF)
def connect_to_network():
    print('Connecting to Network...')
    wlan.active(True)
    wlan.config(pm = 0xa11140) # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        
# Set up Real Time CLock from UTC time server
def setup_RTC():
    try:
        ntptime.settime()
    except OSError:
        print("Time out")
        time.sleep(5)
        ntptime.settime()

async def readbme280():
    global reading
    while True:
        values = bme.values
        reading = f'Temperature: {values[0]}, Humidity: {values[2]}, Pressure: {values[1]}'
        print(reading)
        oled.fill(0)
        oled.text(f"Temp {values[0]}", 0, 0)
        oled.text(f"PA {values[1]}", 0, 20)
        oled.text(f"Humidity {values[2]}", 0,40)
        oled.show()
        await asyncio.sleep(WAIT_READING)

async def serve_client(reader, writer):
    request_line = await reader.readline()
    # print("Request:", request_line)

 # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'.encode())
    writer.write(webpage().encode())

    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    connect_to_network()
    setup_RTC()
    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    asyncio.create_task(readbme280())
    while True:
        onboard.on()
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(WAIT_MAIN)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
