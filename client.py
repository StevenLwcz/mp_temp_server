import asyncio 
import json
import sys

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
     print(x)

asyncio.run(main(sys.argv))
