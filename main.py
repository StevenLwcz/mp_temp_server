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

WAIT_TEMP = const(30) # 30 seconds for testing will be 10 to 15 min 
WAIT_LOOP = const(10) # 10 seconds for testing will be longer later

led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)

tempDisplay = TempDisplay(ssid)

tempDisplay.text("Connecting to {ssid}")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#TODO catch time out exception
ntptime.settime()
#TODO adjust for BST

# TODO send connection info to oled
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print("Waiting for connection...")
    tempDisplay.text("Waiting {ssid} {max_wait}")
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError("network connection failed")
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

tempDisplay.setWlan(wlan)

# sensor_temp = machine.ADC(4)
# conversion_factor = const(5.035477e-05) # 3.3 / (65535)

# Assume OLED and BME280 will share the same i2c pins
bme = bme280.BME280(i2c=tempDisplay.i2c)
print(bme.values)

templist = []

async def readtemp():
    while True:
        await asyncio.sleep(WAIT_TEMP)
        # sensor = sensor_temp.read_u16()
        # reading = sensor * conversion_factor 
        # temperature = 27 - (reading - 0.706)/0.001721
        # templist.append((time.mktime(time.localtime()), temperature))
        # tempDisplay.temperature(temperature)
        bme = bme280.BME280(i2c=i2c)
        tempDisplay.env_data(bme.values)
        print(bme.values)
        templist.append((time.mktime(time.localtime()), bme.values))
        # print(sensor, temperature)

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
    while True:
        onboard.on()
        lt = time.localtime()
        print(f"Time: {lt[3]}:{lt[4]}:{lt[5]}")
        print(f"Len: {len(templist)}")
        print(f"Alloc: {gc.mem_alloc() / 1024}  Free: {gc.mem_free() / 1024}")
        print(f"Wlan: {wlan.status()}")
        # update oled with status ?
        tempDisplay.time_date()
        tempDisplay.wlan_status()
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(WAIT_LOOP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Bye!')
finally:
    print("finally")
    asyncio.new_event_loop()
