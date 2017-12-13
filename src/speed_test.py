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


class genericPage(object):
    """Defines the basic page object and the methods it should have."""

    def receive_signal(self, signal):
        print("method receive_signal not defined")

    @if_free
    def display(self):
        print("method display not defined")

    @if_free
    def change_page(self, page):
        page = page(*args, **kwargs)

    def update_state(self):
        print("method update_state not defined")

    def update_page(self):
        print("method update_page not defined")


class mainPage(genericPage):
    """Object that represents the main page, which shows general system
       information."""

    def __init__(self, nanohat):
        self.state = 0

    def receive_signal(self, signal):
        # if lock pass
        # else
        if signal == signal.SIGUSR1:
            print("K1 pressed")
            pass
        elif signal == signal.SIGUSR2:
            print("K2 pressed")
            self.change_page(testPage)
        elif signal == signal.SIGALRM:
            print("K3 pressed")
            self.change_page(shutdownPage)

    @if_free
    def display(self):
        self._update_data()
        text = "IP: {0}".format(self.ip_addr)
        self.draw.text((1, 1), text, font=font10b, fill=255)
        text = "ip"
        self.draw.text((4, 51), text, font=self.nanohat.font10b, fill=255)
        text = "test"
        self.draw.text((51, 51), text, font=self.nanohat.font10b, fill=255)
        text = "sd"
        self.draw.text((111, 51), text, font=self.nanohat.font10b, fill=255)
        oled.drawImage(self.nanohat.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def _update_data(self):
        self.ip_addr = get_ip()


class testPage(genericPage):
    """Represents the test page, which is responsible for running tests."""

    def __init__(self):
        pass

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


class shutdownPage(genericPage):
    """Represents the shutdown page, which takes care of shutting the
       system down."""

    def __init__(self):
        pass

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
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        oled.drawImage(self.image)
        #self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        os.system('sudo poweroff')


def telusSlogan():
    """Prints the Telus slogan"""
    draw.text((27, 1), "TELUS", font=font24b, fill=255)
    draw.text((23, 31), "The Future", font=font14, fill=255)
    draw.text((20, 45), "is Friendly", font=font14, fill=255)
    oled.drawImage(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)


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


def if_free(func):
    """Made to be used as a decorator on functions that require locked to be free"""
    if not locked:
        locked = True
        func(*args, **kwargs)
        locked = False


def periodic_display():
    while True:
        page.display()
        time.sleep(0.5)


def receiveSignal(signum, stack):
    """Called whenever a signal is received."""
    threading.Thread(target=page.receive_signal, args=[signum])


if __name__ == "__main__":

    # initialization of constants
    width = 128
    height = 64
    padding = 1
    iperf_duration = 10
    iperf_server = '192.168.1.72'
    locked = False

    # initialization of display
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    font10b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10)
    font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14)
    font14b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14)
    font24b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24)
    oled.init()
    oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
    oled.setHorizontalMode()
    telusSlogan()
    time.sleep(2)

    # assign receiveSignal to be called when buttons are pressed
    signal.signal(signal.SIGUSR1, receiveSignal) # button 1 (left)
    signal.signal(signal.SIGUSR2, receiveSignal) # button 2 (middle)
    signal.signal(signal.SIGALRM, receiveSignal) # button 3 (right)

    page = mainPage()
    # spawn display thread
    threading.Thread(target=periodic_display)

    while True:
        signal.pause()
