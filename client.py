import asyncio 
import json
import sys
from time import time, ctime

def get_time(data):
    return data[0]

def get_temp(data):
    return data[1]

def get_press(data):
    return data[2]

def get_humid(data):
    return data[3]

# tuple of ((time, value), (time, value))
def get_min_max(data, fn):
    min_value = min(data, key=fn, default=0)
    max_value = max(data, key=fn, default=0)
    return (ctime(min_value[0]), fn(min_value)), (ctime(max_value[0]), fn(max_value))

async def temp_client(message, address, port): 
     print(f'Send:{message!r}')
     reader, writer = await asyncio.open_connection(address, port)
     writer.write(message.encode())
     await writer.drain()

     data = await reader.readline()
     # print(f'Received: {data.decode()!r}')
     writer.close() 
     await writer.wait_closed()
     return data

async def main(argv):
     if len(argv) < 3:
         print("client address port")
         exit()

     address = argv[1]
     port = argv[2]
     message = "GETTEMP\n"
     data = await temp_client(message, address, port)
     x = json.loads(data)
     print(x)
     min_value, max_value = get_min_max(x, get_temp) 
     print(f'Temp - min: {min_value[0]}, {min_value[1]}, max: {max_value[0]}, {max_value[1]}')

     min_value, max_value = get_min_max(x, get_press) 
     print(f'Pres - min: {min_value[0]}, {min_value[1]}, max: {max_value[0]}, {max_value[1]}')

     min_value, max_value = get_min_max(x, get_humid) 
     print(f'Himi - min: {min_value[0]}, {min_value[1]}, max: {max_value[0]}, {max_value[1]}')

asyncio.run(main(sys.argv))
