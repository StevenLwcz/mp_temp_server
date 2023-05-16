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
WAIT_LOOP = const(400) # 1 mins

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

@micropython.native
async def readtemp():
    while True:
        result = [None, None, None]
        if len(templist) >= 250:
            del templist[:10]
                         
        free = gc.mem_free() / 1024
        lt = time.localtime()
        bme.read_compensated_data(result)
        data = [time.mktime(lt), round(result[0], 2), round(result[1], 1), round(result[2], 1), round(free, 1)]
        templist.append(data)
        tempDisplay.env_data(result)
        tempDisplay.updateGraphs(templist)
        print(f"Time: {lt[3]:02}:{lt[4]:02}:{lt[5]:02} Len: {len(templist)}")
        print(data)
        await asyncio.sleep(WAIT_TEMP)
        
async def update_time():
    while True:
        lt = time.localtime()
        sec = lt[5]
        tempDisplay.time_date()
        tempDisplay.wlan_update_status()
        await asyncio.sleep(60 - sec)
        
        
@micropython.native
async def temp_server(reader: StreamReader, writer: StreamWriter):
    try:
        request_line = await reader.readline()
        lt = time.localtime()
        print(f"Request: {request_line} - {lt[3]:02}:{lt[4]:02}:{lt[5]:02} {reader.get_extra_info('peername')}")
        if len(request_line) == 0:
            pass
        else:
            request = request_line.decode()
            request = request.split()
            if request[0] == 'GET' and request[2] == 'HTTP/1.1':
                json_request = False;
              
                while True:
                    line = await reader.readline()
                    if json_request == False and line == b'Accept: application/json\r\n':
                        print("JSON Request")
                        json_request = True
                    elif line == b'\r\n':
                        break
                        
                if json_request: 
                    writer.write(b'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n')
                    writer.write(b'Access-Control-Allow-Origin: *\r\n\r\n')
                    await writer.drain()
                    writer.write(str.encode(json.dumps(templist, separators=(',',':'))))    
                else:
                    file = request[1]
                    if file == "/":
                        file = "/web/index.html"
                    else:
                        file = "/web" + file 
                    try:
                        with open(file, "r") as fd:
                            writer.write(b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                            await writer.drain()          
                            writer.write(fd.read().encode())
                    except:
                        writer.write(b'HTTP/1.0 404 Not Found\r\n\r\n')
            else: # client
                writer.write(str.encode(json.dumps(templist, separators=(',',':')))) 
                writer.write(b'\n')

        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except asyncio.CancelledError:
        print('Connection dropped!')
    
@micropython.native
async def main(host='0.0.0.0', port=65510):
    asyncio.create_task(asyncio.start_server(temp_server, host, port))
    asyncio.create_task(readtemp())
    asyncio.create_task(update_time())
    while True:
        onboard.on()
        await asyncio.sleep(0.25)
        prevfree = gc.mem_free() / 1024
        gc.collect()
        free = gc.mem_free() / 1024
        print(f"Alloc: {gc.mem_alloc() / 1024}  Free: {free} ({prevfree})")
        onboard.off()
        await asyncio.sleep(WAIT_LOOP)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('CTRL-C Pressed')
finally:
    print("finally")
    asyncio.new_event_loop()
