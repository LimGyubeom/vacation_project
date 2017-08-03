#! /usr/bin/python
#-*- coding: utf-8 -*-

# https://github.com/Mic92/python-mpd2

from oled.serial import i2c, spi
from oled.device import sh1106, ssd1306
from oled.render import canvas

import os, sys, time
from PIL import ImageFont

from mpd import MPDClient, MPDError, CommandError

reload(sys)
sys.setdefaultencoding('utf-8')

os.environ["LC_COLLATE"] = "ko_KR.UTF-8"

#---------------------------------------------------------------------

class PollerError(Exception):
    """Fatal error in poller."""

class MPDPoller(object):
    def __init__(self, host="localhost", port="6600", password=None):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()

    def connect(self):
        try:
            self._client.connect(self._host, self._port)
        # Catch socket errors
        except IOError as err:
            errno, strerror = err
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, strerror))

        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as e:
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, e))

        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as e:
                raise PollerError("Could not connect to '%s': "
                                  "password commmand failed: %s" %
                                  (self._host, e))

            # Catch all other possible errors
            except (MPDError, IOError) as e:
                raise PollerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, e))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()

        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()

    def poll(self):
        try:
            song = self._client.currentsong()

        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()

            try:
                self.connect()

            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)

            try:
                song = self._client.currentsong()

            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve current song: %s" % e)

        # Hurray!  We got the current song without any errors!
	return song

#---------------------------------------------------------------------

gulim14 = ImageFont.truetype('/home/pi/fonts/NGULIM.TTF', 12)
Mine = ImageFont.truetype('/home/pi/fonts/Minecraftia-Regular.ttf', 12)
import datetime
import thread

disp_mode_fifo = '/tmp/raw_fifo'
raw_disp_mode = ""
def get_disp_mode_thread():
    global raw_disp_mode

    # disp_mesg fifo 생성
    if not os.path.exists(disp_mode_fifo):
        os.mkfifo(disp_mode_fifo)

    # keep waiting for fifo input
    while True:
        fd = open(disp_mode_fifo, 'r')
        while True:
            data = fd.read()
            if len(data) == 0: break
            raw_disp_mode = data

def main():
    poller = MPDPoller()
    poller.connect() 
    #disp_mode를 받기위해 named pipe read 대기하는 thread
    thread.start_new_thread(get_disp_mode_thread, ())

    while True:
        song = poller.poll()
        #print song
        if raw_disp_mode == 'clock':
            now = datetime.datetime.now()
            nowDatetime = now.strftime('%Y-%m-%d %a')
            nowDatetime1 = now.strftime ('%H:%M:%S')
            with canvas(device) as draw:
                #try:
                    print (nowDatetime +'   '+nowDatetime1)
                    draw.text((0, 0), nowDatetime, font=Mine, fill='white')
                    draw.text((0, 16), nowDatetime1 , font=Mine, fill='white')
                #except: pass
            time.sleep(1)
        elif raw_disp_mode == 'mpd':
             with canvas (device) as draw:
                 #try:
                     name = song['file']
                     #print song
                     print unicode(name)
                     #title = song['title']
                     draw.text((0, 0),unicode(name), font=Mine, fill='white')
                     #draw.text((0, 16),unicode(title), font=Mine, fill='white')
                 #except: pass
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

