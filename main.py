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

WAIT_TEMP = const(360) # 6 mins 
WAIT_LOOP = const(900) # 15 mins

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

try:
    ntptime.settime()
except OSError:
    print("Time out")
    time.sleep(5)
    ntptime.settime()

# Assume OLED and BME280 will share the same i2c pins
bme = bme280.BME280(i2c=tempDisplay.i2c)
print(bme.values)

templist = []
tempDisplay.initGraphs()

async def readtemp():
    while True:
        result = [None, None, None]
        if len(templist) >= 250:
            del templist[:10]
                         
        free = gc.mem_free() / 1024
        lt = time.localtime()
        bme.read_compensated_data(result)
        rdata = [round(result[0], 2), round(result[1], 1), round(result[2], 1), round(free, 1)]
        templist.append((time.mktime(lt), rdata))
        tempDisplay.env_data(result)
        tempDisplay.updateGraphs(templist)
        print(f"Time: {lt[3]:02}:{lt[4]:02}:{lt[5]:02} Len: {len(templist)}")
        print(rdata)
        await asyncio.sleep(WAIT_TEMP)
        
async def update_time():
    while True:
        lt = time.localtime()
        sec = lt[5]
        # print(f"Time: {lt[3]:02}:{lt[4]:02}:{lt[5]:02} Len: {len(templist)}")
        tempDisplay.time_date()
        tempDisplay.wlan_update_status()
        await asyncio.sleep(60 - sec)

async def temp_server(reader: StreamReader, writer: StreamWriter):
    try:
        data = await reader.readline()
        print(data)
        # if data = "GETTEMP" ...
        if data == b'GET / HTTP/1.1\r\n':
        
            while await reader.readline() not = b'\r\n'
           
            writer.write(b'HTTP/1.0 200 OK\r\n')
            writer.write(b'Content-type: application/json\r\n')
            writer.write(b'Access-Control-Allow-Origin: *\r\n')
            writer.write(b'\r\n')
            
        bytes = str.encode(json.dumps(templist))
        writer.write(bytes)
        writer.write(b'\n') 
        await writer.drain()
        writer.close()
        await writer.wait_closed()
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
        # if free < 80:
        gc.collect()
        free = gc.mem_free() / 1024
        print(f"Alloc: {gc.mem_alloc() / 1024}  Free: {free}*")

        onboard.off()
        await asyncio.sleep(WAIT_LOOP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('CTRL-C Pressed')
finally:
    print("finally")
    asyncio.new_event_loop()
