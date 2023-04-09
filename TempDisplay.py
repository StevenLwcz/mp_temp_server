from micropython import const
from machine import Pin, I2C
import utime as time
import ssd1306

OLED_WIDTH = const(128)
OLED_HEIGHT = const(32)

day = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
mon = ["Ja", "Fe", "Ma", "Ap", "Ju", "Jl", "Au", "Se", "Oc", "No", "De"]

# 16 x 4 characters
# ----------|------
# HH:MM DD dd MM YY      
# temp      |      
# 10123.4hPa| graphs   
# humidity  |    
# ----------|------

OLED_TIME_X = const(0)
OLED_TIME_Y = const(0)
OLED_TIME_W = const(128)
OLED_TIME_H = const(8)

OLED_WLAN_X = const(112)
OLED_WLAN_Y = const(16)
OLED_WLAN_H = const(16)
OLED_WLAN_W = const(16)

OLED_IP_X = const(0)
OLED_IP_Y = const(24)
OLED_IP_H = const(7)
OLED_IP_W = const(128)

OLED_ENV_X = const(0)
OLED_ENV_Y = const(8)
OLED_ENV_H = const(24)
OLED_ENV_W = const(80)

class TempDisplay(object):

    display = None
    i2c = None
    ip = None
    rssi = None
    ssid = None
    wlan = None

    def __init__(self, ssid):
        self.ssid = ssid
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1))
        print(self.i2c.scan())
        self.display = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self.i2c)
       
    def setWlan(self, wlan):
        self.wlan = wlan
        self.ip = wlan.ifconfig()[0]
        self.display.fill_rect(OLED_IP_X, OLED_IP_Y, OLED_IP_W, OLED_IP_H, 0)
        self.display.text(self.ip, OLED_IP_X, OLED_IP_Y)
        self.display.show()
        
    def wlan_update_status(self):
        signal_level = 0
        if self.wlan.status() == 3:
            if self.rssi:
                 signal_level = (self.rssi + 100) * 16 // 100
            else:
                print(f"Scanning for {self.ssid}")
                wl = self.wlan.scan() # only get resieved signal level once because it takes time
                if wl == []:
                    signal_level = OLED_WLAN_H
                else:
                    self.rssi = [x[3] for x in wl if x[0] == self.ssid.encode()][0]
                    signal_level = (self.rssi + 100) * 2 // 25
        else:
            self.rssi = None

        print(f'Signal level: {signal_level} Wlan: {self.wlan.status()}')
        self.display.fill_rect(OLED_WLAN_X, OLED_WLAN_Y, OLED_WLAN_W, OLED_WLAN_H, 0)
        for i in range(signal_level + 1):
            self.display.vline(OLED_WLAN_X + i, OLED_WLAN_Y + OLED_WLAN_H - i, i, 1)

        self.display.show()

    def time_date(self):
        lt = time.localtime()
        d1 = day[lt[6]]
        mo = mon[lt[1] - 1]
        ye = str(lt[0])[2:4]
        d2 = f'{lt[2]:02}'
        ti = f'{lt[3]:02}:{lt[4]:02}'
        
        self.display.fill_rect(OLED_TIME_X, OLED_TIME_Y, OLED_TIME_W, OLED_TIME_H, 0)
        self.display.text(ti, OLED_TIME_X, OLED_TIME_Y, 1)
        self.display.text(d1, OLED_TIME_X + 44, OLED_TIME_Y, 1)
        self.display.text(d2, OLED_TIME_X + 64, OLED_TIME_Y, 1)
        self.display.text(mo, OLED_TIME_X + 84, OLED_TIME_Y, 1)
        self.display.text(ye, OLED_TIME_X + 104, OLED_TIME_Y, 1)
        self.display.show()

    def env_data(self, data):
        self.display.fill_rect(OLED_ENV_X, OLED_ENV_Y, OLED_ENV_W, OLED_ENV_H, 0)
        self.display.text(f'{data[0]:.1f}C', OLED_ENV_X, OLED_ENV_Y)
        self.display.text(f'{data[1]:.1f}P', OLED_ENV_X, OLED_ENV_Y + 8)
        self.display.text(f'{data[2]:.2f}%', OLED_ENV_X, OLED_ENV_Y + 16)
        self.display.show()
        
    def text(self, txt):
        self.display.fill(0)
        self.display.text(txt, 0, 0)
        self.display.show()
