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
import iperf3


class NanoHatOled(object):
    """Object for interfacing to the nanohat's OLED display and buttons."""
    
    def __init__(self):
        self.width = 128
        self.height = 64
        self.padding = 1
        self.page = 0
        self.iperf_duration = 10
        self.iperf_server = '192.168.1.72'
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
        elif self.page == 2: # shut down check page
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

    def telusSlogan(self):
        """Prints the Telus slogan"""
        self.draw.text((self.padding+26, self.padding), "TELUS", font=self.font24b, fill=255)
        self.draw.text((self.padding+22, self.padding+30), "The Future", font=self.font14, fill=255)
        self.draw.text((self.padding+19, self.padding+44), "is Friendly", font=self.font14, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

            
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
        text = "Testing down..."
        self.draw.text((self.padding, self.padding+20), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do down test
        down_client = iperf3.Client()
        down_client.duration = self.iperf_duration
        down_client.server_hostname = self.iperf_server
        down_client.reverse = True
        result = down_client.run()
        #down = int(round(result.sent_Mbps))
        down = result.sent_Mbps
        # display 'testing up'
        text = "Testing up..."
        self.draw.text((self.padding, self.padding+20), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do up test
        up_client = iperf3.Client()
        up_client.duration = self.iperf_duration
        up_client.server_hostname = self.iperf_server
        up_client.reverse = False
        result = up_client.run()
        #up = int(round(result.sent_Mbps))
        up = result.sent_Mbps
        # display 'testing jitter'
        text = "Testing jitter..."
        self.draw.text((self.padding, self.padding+20), text,  font=self.font14b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        # do jitter test
        j_client = iperf3.Client()
        j_client.duration = self.iperf_duration
        j_client.server_hostname = self.iperf_server
        j_client.reverse = False
        j_client.protocol = 'udp'
        result = j_client.run()
        jitter = result.jitter_ms
        # display results
        text = "down: {:.0f} Mbit/s".format(down)
        self.draw.text((self.padding, self.padding), text,  font=self.font10b, fill=255)
        text = "up: {:.0f} Mbit/s".format(up)
        self.draw.text((self.padding, self.padding+12), text,  font=self.font10b, fill=255)
        text = "jitter: {:.3f} ms".format(jitter)
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
        text = "Shut down?"
        self.draw.text((self.padding+20, self.padding+18), text,  font=self.font14b, fill=255)
        text = "yes"
        self.draw.text((self.padding+3, self.padding+50), text,  font=self.font10b, fill=255)
        text = "no"
        self.draw.text((self.padding+110, self.padding+50), text,  font=self.font10b, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def shutDown(self):
        """Actual shut down page"""
        #text = "shutting down..."
        #self.draw.text((self.padding, self.padding+30), text,  font=self.font14b, fill=255)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        oled.drawImage(self.image)
        #self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        os.system('sudo poweroff')


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
