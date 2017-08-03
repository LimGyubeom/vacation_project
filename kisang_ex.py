#!/usr/bin/python
#-*- coding: utf-8 -*-

from oled.serial import i2c, spi
from oled.device import sh1106, ssd1306
from oled.render import canvas

import sys, subprocess, os
import requests
import time
import datetime
from PIL import ImageFont
import fonts
import thread

reload(sys)
sys.setdefaultencoding( 'utf-8' )

now = datetime.datetime.now()
if now.minute < 35:
    now = now - datetime.timedelta(hours=1)
ymd = str(now.year) + str('%02d' % now.month) + str('%02d' % now.day)
hour = str('%02d' % now.hour) + '00'
homex = '68'
homey = '100'

weatherUrlBase = 'http://newsky2.kma.go.kr/service/SecndSrtpdFrcstInfoService2/ForecastGrib'
Servicekey = 'v5am6iSNaarfzPqtr%2FJQ7%2BUKWInoHUBn%2BH6MCS72%2BZPliNo9sC9tJxB0yxg%2B0KrvJNuTOqf3ZitqKPyXdcongQ%3D%3D'
url = weatherUrlBase + '?ServiceKey=' + Servicekey + '&base_date=' + ymd + '&base_time=' + hour + '&nx=' + homex + '&ny=' + homey + '&_type=json'
r = requests.get(url)
#print url
#print r.json()

tmp = {}
for data in r.json()['response']['body']['items']['item']:
    tmp[data['category']] = data['obsrValue']

tem = str(tmp['T1H'])
hum = str(tmp['REH'])

print u'온도:' + tem
print u'습도:' + hum

Mine = ImageFont.truetype('/home/pi/fonts/Minecraftia-Regular.ttf', 12)
gulim12 = ImageFont.truetype('/home/pi/fonts/NGULIM.TTF', 12)

def main():
    with canvas(device) as draw:
        draw.text((0, 0), u' 온도:' + tem, font = gulim12, fill = 'white')
        draw.text((0, 16), u' 습도:' + hum, font = gulim12, fill = 'white')
    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        device = sh1106(i2c(port=1, address=0x3c))
    except IOError:
        try:
            device = sh1106(spi(device=0, port=0))
        except IOError:
            sys.exit(1)

    main()
