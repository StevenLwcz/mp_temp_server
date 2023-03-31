### Using Micropython and a Pico W to build a simple temperature server

The client is written in Rust (Python version pending).  The server uses a ssd3106 OLED 128x32 display and a BME280 environment sensor.

### Aim
The server will collect readings over a 24hr period and when requested by the client send the data to the client in JSON format for further processing.

Work in progress...

### Used by this project:

    bme280_float.py from https://github.com/robert-hh/BME280.git
    ssd1306.py from https://github.com/stlehmann/micropython-ssd1306.git
 
### To Use

1 Create a wlanc.py

    password = "Your WLAN password"
    ssid = "your SSID"

Don't put your wlanc.py on github or anywhere on the internet. The .gitignore already has an entry for wlanc.py.

2 Upload wlanc.py main.py and TempDisplay.py as well as the above two Python files to your Pico W using Thonny

I assume you are already familaur with the basic of using a Pico W. See Raspberry Pi Pico Docs for more info if needed.

### TODO

1. Make sure long runing server does not run out of memory
1. Various tidy ups/refinements
1. Improve client
1. Provide Python client version
