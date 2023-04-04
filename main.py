import time
import network
import uasyncio as asyncio
import ntptime
import utime as time
from uasyncio import StreamReader, StreamWriter
import ujson as json
import gc
from machine import Pin, I2C
from wlanc import ssid, password
from TempDisplay import TempDisplay
import bme280_float as bme280

WAIT_TEMP = const(300) # 30 seconds for testing will be 10 to 15 min 
WAIT_LOOP = const(600) # 10 seconds for testing will be longer later

led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)

tempDisplay = TempDisplay(ssid)

tempDisplay.text(f"WLAN: {ssid}")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# TODO send connection info to oled
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("Waiting for connection...")
    time.sleep(1)
    tempDisplay.text("Waiting {ssid} {max_wait}")

if wlan.status() != 3:
    tempDisplay.text("Failed to connect")
    raise RuntimeError("network connection failed")
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

tempDisplay.setWlan(wlan)

#TODO catch time out exception
try:
    ntptime.settime()
except OSError:
    ntptime.settime()
#TODO adjust for BST

# Assume OLED and BME280 will share the same i2c pins
bme = bme280.BME280(i2c=tempDisplay.i2c)
print(bme.values)

templist = []

async def readtemp():
    while True:
        result = [None, None, None]
        bme.read_compensated_data(result)
        tempDisplay.env_data(result)
        print(result)
        templist.append((time.mktime(time.localtime()), result))
        await asyncio.sleep(WAIT_TEMP)
        
async def update_time():
    while True:
        lt = time.localtime()
        sec = lt[5]
        print(f"Time: {lt[3]:02}:{lt[4]:02}:{lt[5]:02} Len: {len(templist)}")
        tempDisplay.time_date()
        tempDisplay.wlan_update_status()
        await asyncio.sleep(60 - sec)

async def temp_server(reader: StreamReader, writer: StreamWriter):
    print('New connection. with json')
    # jdata = ujson.dumps(templist)
    try:
        data = await reader.readline()
        print(data)
        # if data = "GETTEMP" ...
        bytes = str.encode(json.dumps(templist))
        writer.write(bytes)
        writer.write(b'\n') 
        await writer.drain()
        print('Leaving Connection.')
    except asyncio.CancelledError:
        print('Connection dropped!')

async def main(host='0.0.0.0', port=65510):
    asyncio.create_task(asyncio.start_server(temp_server, host, port))
    asyncio.create_task(readtemp())
    asyncio.create_task(update_time())
    while True:
        onboard.on()
        await asyncio.sleep(0.25)
       
        free = gc.mem_free() / 1024
        print(f"Alloc: {gc.mem_alloc() / 1024}  Free: {free}")
        if free < 80:
            gc.collect()
        onboard.off()
        await asyncio.sleep(WAIT_LOOP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('CTRL-C Pressed')
finally:
    print("finally")
    asyncio.new_event_loop()
