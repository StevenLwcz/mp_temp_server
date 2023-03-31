### Using Micropython and a Pico W to build a simple temperature server

The client is written in Rust (Python version pending).  The server uses a ssd3106 OLED 128x32 display and a BME280 environment sensor.

### Aim
The server will collect readings over a 24hr period and when requested by the client send the data to the client in JSON format for further processing.

Work in progress...

### Used by this project:

    bme280_float.py from https://github.com/robert-hh/BME280.git
    ssd1306.py from https://github.com/stlehmann/micropython-ssd1306.git
 
### TODO

1. Make sure long runing server does not run out of memory
1. Various tidy ups/refinements
1. Improve client
1. Provide Python client version
