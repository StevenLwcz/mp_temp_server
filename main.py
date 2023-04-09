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
import micropython

OLED_MAX_Y = const(31)

WAIT_TEMP = const(300) # 5 mins 
WAIT_LOOP = const(300) # 5 mins

led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT, value=0)

tempDisplay = TempDisplay(ssid)

tempDisplay.text(f"WLAN: {ssid}")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

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
    print("TIME OUT")
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
       # tempDisplay.wlan_update_status()
        await asyncio.sleep(60 - sec)

async def temp_server(reader: StreamReader, writer: StreamWriter):
    print('New connection. with json')
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
    
def get_temp(data):
    return data[1][0]

# Fit temp range into 24 pixels height
def graph_scale(min, max):
    diff = max - min
    if diff <= 0.2875:
        return 80
    if diff <= 0.575:
        return 40
    if diff <= 1.15:
        return 20
    if diff <= 2.3:
        return 10
    if diff <= 4.6:
        return 5
    if diff<= 9.2:
        return 2.5
    if diff <= 18.4:
        return 1.25
    if diff <= 23:
        return 1
    if diff <= 62:
        return 0.5
    return 0.25

def display_temp_graph():
    min_temp = get_temp(min(templist, key=get_temp, default=0))
    max_temp = get_temp(max(templist, key=get_temp, default=0))
    scale = graph_scale(min_temp, max_temp)
    x = 80
    length = -48 if len(templist) >= 48 else 0
    print("Graph ", min_temp, max_temp, len(templist), scale)
    tempDisplay.display.fill_rect(80, 8, 48, 24, 0)
    for data in templist[length:]:
        y = OLED_MAX_Y - int((get_temp(data) - min_temp) * scale)
        print(y, end=' ')
        tempDisplay.display.pixel(x, y, 1)
        x += 1
        
    print("")
    tempDisplay.display.show()
        
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
            micropython.mem_info()
            gc.collect()
            print(f"Alloc: {gc.mem_alloc() / 1024}  Free: {free}*")

        onboard.off()
        display_temp_graph()
        await asyncio.sleep(WAIT_LOOP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('CTRL-C Pressed')
finally:
    print("finally")
    asyncio.new_event_loop()
