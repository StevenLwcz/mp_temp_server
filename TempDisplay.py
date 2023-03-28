from micropython import const
from machine import Pin, I2C
import utime as time
import ssd1306

OLED_WIDTH = const(128)
OLED_HEIGHT = const(32)

# 16 x 4 characters
# ----------------
# time and date  W
# temp
#
# ip address
# ----------------

OLED_TIME_X = const(0)
OLED_TIME_Y = const(0)
OLED_TIME_W = const(14 * 8)
OLED_TIME_H = const(7)

OLED_WLAN_X = const(119)
OLED_WLAN_Y = const(0)
OLED_WLAN_H = const(8)
OLED_WLAN_W = const(8)

OLED_TEMP_X = const(0)
OLED_TEMP_Y = const(8)
OLED_TEMP_W = const(64)
OLED_TEMP_H = const(7)

OLED_IP_X = const(0)
OLED_IP_Y = const(24)
OLED_IP_H = const(7)
OLED_IP_W = const(128)

class TempDisplay(object):

    display = None
    i2c = None
    ip = None
    rssi = None
    ssid = None
    wlan = None

    def __init__(self, wlan, ssid):
        self.ssid = ssid
        self.wlan = wlan
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1))
        self.display = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self.i2c)
        self.ip = wlan.ifconfig()[0]

    def wlan_status(self):
        signal_level = 0
        if self.wlan.status() == 3:
            if self.rssi:
                 signal_level = (self.rssi + 100) * 2 // 25
            else:
                print(f"Scanning for {self.ssid}")
                wl = self.wlan.scan() # only get resieved signal level once because it takes time
                if wl == []:
                    signal_level = 8
                else:
                    print("wl", wl)
                    self.rssi = [x[3] for x in wl if x[0] == self.ssid.encode()][0]
                    signal_level = (self.rssi + 100) * 2 // 25
        else:
            self.rssi = None
       
        print(f'Signal level {signal_level}')
        self.display.fill_rect(OLED_WLAN_X, OLED_WLAN_Y, OLED_WLAN_W, OLED_WLAN_H, 0)
        self.display.fill_rect(OLED_WLAN_X, OLED_WLAN_Y, OLED_WLAN_W, signal_level, 1)
        self.display.fill_rect(OLED_IP_X, OLED_IP_Y, OLED_IP_W, OLED_IP_H, 0)
        self.display.text(self.ip, OLED_IP_X, OLED_IP_Y)
        self.display.show()

    def time_date(self):
        # getlocal time convert to HH:MM Dy Mh Yr
        lt = time.localtime()
        self.display.fill_rect(OLED_TIME_X, OLED_TIME_Y, OLED_TIME_W, OLED_TIME_H, 0)
        self.display.text(f"{lt[3]:02}:{lt[4]:02}", OLED_TIME_X, OLED_TIME_Y, 1)
        self.display.hline(OLED_TIME_X, OLED_TIME_H, OLED_WIDTH, 1)
        self.display.show()

    def temperature(self, temp):
        self.display.fill_rect(OLED_TEMP_X, OLED_TEMP_Y, OLED_TEMP_W, OLED_TEMP_H, 0)
        self.display.text(str(temp), OLED_TEMP_X, OLED_TEMP_Y)
        self.display.show()