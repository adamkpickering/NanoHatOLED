#!/usr/bin/env python
#
#

import bakebit_128_64_oled as oled
from PIL import Image, ImageFont, ImageDraw
import time
import sys
import subprocess
import threading
import signal
import os
import socket


class NanoHatOled(object):
    """Object for interfacing to the nanohat's OLED display and buttons."""
    
    def __init__(self):
        self.width = 128
        self.height = 64
        self.padding = 1
        self.page = 0
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font10b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10)
        self.font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
        self.font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14)
        self.font14b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14)
        self.font24b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24)
        oled.init()
        oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
        oled.setHorizontalMode()
        self.telusSlogan()
        time.sleep(2)
        self.ipPage()
        signal.signal(signal.SIGUSR1, self.receiveSignal) # button 1 (left)
        signal.signal(signal.SIGUSR2, self.receiveSignal) # button 2 (middle)
        signal.signal(signal.SIGALRM, self.receiveSignal) # button 3 (right)

    def receiveSignal(self, signum, stack):
        """Called whenever a signal is received."""
        if self.page == 0: # default page, get and display IP
            if signum == signal.SIGUSR1:
                print("K1 pressed")
                self.ipPage()
            elif signum == signal.SIGUSR2:
                print("K2 pressed")
                self.testPage()
            elif signum == signal.SIGALRM:
                print("K3 pressed")
                self.sdPage()
            else:
                pass
        elif self.page == 1: # iperf test page
            if signum == signal.SIGUSR1:
                print("K1 pressed")
                self.ipPage()
            elif signum == signal.SIGUSR2:
                print("K2 pressed")
                self.testPage()
            elif signum == signal.SIGALRM:
                print("K3 pressed")
                self.sdPage()
            else:
                pass
        elif self.page == 2: # shut down page
            if signum == signal.SIGUSR1:
                print("K1 pressed")
                self.shutDown()
            elif signum == signal.SIGUSR2:
                print("K2 pressed")
                pass
            elif signum == signal.SIGALRM:
                print("K3 pressed")
                self.ipPage()
            else:
                pass
            
    def ipPage(self):
        """Gets and displays the IP address"""
        # set page to 0
        self.page = 0
        # display 'getting IP...'
        #text = "getting IP..."
        #self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        #oled.drawImage(self.image)
        #self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # get ip
        ip_addr = get_ip()
        # display ip address
        text = "IP: {0}".format(ip_addr)
        self.draw.text((self.padding, self.padding), text,  font=self.font10b, fill=255)
        text = "ip"
        self.draw.text((self.padding+3, self.padding+50), text,  font=self.font10b, fill=255)
        text = "test"
        self.draw.text((self.padding+50, self.padding+50), text,  font=self.font10b, fill=255)
        text = "sd"
        self.draw.text((self.padding+110, self.padding+50), text,  font=self.font10b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def testPage(self):
        """Performs iperf test and displays results"""
        # set page to 1
        self.page = 1
        # display 'testing down...'
        text = "testing down..."
        self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do down test
        down = 855
        # display 'testing up'
        text = "testing up..."
        self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do up test
        up = 904
        # display 'testing jitter'
        text = "testing jitter..."
        self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do jitter test
        jitter = "45%"
        # display results
        text = "down: {0}".format(down)
        self.draw.text((self.padding, self.padding), text,  font=self.font10b, fill=255)
        text = "up: {0}".format(up)
        self.draw.text((self.padding, self.padding+12), text,  font=self.font10b, fill=255)
        text = "jitter: {0}".format(jitter)
        self.draw.text((self.padding, self.padding+24), text,  font=self.font10b, fill=255)
        text = "ip"
        self.draw.text((self.padding+3, self.padding+50), text,  font=self.font10b, fill=255)
        text = "test"
        self.draw.text((self.padding+50, self.padding+50), text,  font=self.font10b, fill=255)
        text = "sd"
        self.draw.text((self.padding+110, self.padding+50), text,  font=self.font10b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def sdPage(self):
        """Shut down check page"""
        # set page to 2
        self.page = 2
        # display page
        text = "shut down?"
        self.draw.text((self.padding+20, self.padding+18), text,  font=self.font14b, fill=255)
        text = "yes"
        self.draw.text((self.padding+3, self.padding+50), text,  font=self.font10b, fill=255)
        text = "no"
        self.draw.text((self.padding+110, self.padding+50), text,  font=self.font10b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def shutDown(self):
        """Actual shut down page"""
        text = "shutting down..."
        self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        os.system('systemctl poweroff')

    def drawPage(self, text_array):
        """The idea here was that you could pass a list of strings and the method would take care of
        everything for you. The first string would go on line 1, the second on line 2, etc. Currently
        unfinished."""
        if len(text_array) == 1:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
        if len(text_array) == 2:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font14, fill=255)
            self.draw.text((self.padding, self.padding+12), text_array[1], font=self.font14, fill=255)
        if len(text_array) == 3:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+12), text_array[1], font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+24), text_array[2],  font=self.font10b, fill=255)
        if len(text_array) == 4:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+12), text_array[1], font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+24), text_array[2],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+36), text_array[3],  font=self.font10b, fill=255)
        if len(text_array) == 5:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+12), text_array[1], font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+24), text_array[2],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+36), text_array[3],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+48), text_array[4],  font=self.font10b, fill=255)
        else:
            pass
        # output finished image to oled
        oled.drawImage(self.image)
        # clear current image (here rather than before to increase responsiveness)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def notDefined(self):
        self.drawPage(["Action", "not defined"])
        time.sleep(2)
        self.telusSlogan()

    def telusSlogan(self):
        self.draw.text((self.padding+26, self.padding), "TELUS", font=self.font24b, fill=255)
        self.draw.text((self.padding+22, self.padding+30), "The Future", font=self.font14, fill=255)
        self.draw.text((self.padding+19, self.padding+44), "is Friendly", font=self.font14, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    # for testing purposes
    def one_line(self):
        self.drawPage(["Line one"])
        time.sleep(2)
        self.telusSlogan()

    # for testing purposes
    def two_lines(self):
        self.drawPage(["Line one",
                       "Line four"])
        time.sleep(2)
        self.telusSlogan()

    # for testing purposes
    def three_lines(self):
        self.drawPage(["Line one",
                       "Line two",
                       "Line three"])
        time.sleep(2)
        self.telusSlogan()

    # for testing purposes
    def four_lines(self):
        self.drawPage(["Line one",
                       "Line two",
                       "Line three",
                       "Line four"])
        time.sleep(2)
        self.telusSlogan()


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



#while True:
#    try:
#        draw_page()
#
#        lock.acquire()
#        page_index = pageIndex
#        lock.release()
#
#        if page_index==5:
#            time.sleep(2)
#            while True:
#                lock.acquire()
#                is_drawing = drawing
#                lock.release()
#                if not is_drawing:
#                    lock.acquire()
#                    drawing = True
#                    lock.release()
#                    oled.clearDisplay()
#                    break
#                else:
#                    time.sleep(.1)
#                    continue
#            time.sleep(1)
#            os.system('systemctl poweroff')
#            break
#        time.sleep(1)
#    except KeyboardInterrupt:                                                                                                          
#        break                     
#    except IOError:                                                                              
#        print ("Error")

if __name__ == "__main__":
    nanohat = NanoHatOled()
    while True:
        signal.pause()
