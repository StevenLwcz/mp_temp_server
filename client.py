import asyncio 
import json
import sys

def get_temp(data):
    return data[1][0]

def get_press(data):
    return data[1][1]

def get_humid(data):
    return data[1][2]

def get_min_max(data, fn):
    return fn(min(data, key=fn, default=0)), fn(max(data, key=fn, default=0))

async def temp_client(message, address, port): 
     print(f'Send:{message!r}')
     reader, writer = await asyncio.open_connection(address, port)
     writer.write(message.encode())
     await writer.drain()

     data = await reader.readline()
     # print(f'Received: {data.decode()!r}')
     print('Close the connection') 
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
     min_value, max_value = get_min_max(x, get_temp) 
     print(f'Temp - min: {min_value} max: {max_value}')
     min_value, max_value = get_min_max(x, get_press) 
     print(f'Pres - min: {min_value} max: {max_value}')
     min_value, max_value = get_min_max(x, get_humid) 
     print(f'Humi - min: {min_value} max: {max_value}')

asyncio.run(main(sys.argv))
