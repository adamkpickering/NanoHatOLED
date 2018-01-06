#!/usr/bin/env python
#
#

import bakebit_128_64_oled as oled
from PIL import Image, ImageFont, ImageDraw
import time
import datetime
import sys
import subprocess
import threading
import thread
import signal
import os
import socket
import iperf3
from subprocess import Popen, PIPE, STDOUT
import re


def check_lock_blocking(func):
    """Decorator for functions that require lock to be free. Blocks until the lock is free."""
    def wrapper(*args, **kwargs):
        lock.acquire(1) # nonzero argument means blocking
        func(*args, **kwargs)
        lock.release()
    return wrapper


def check_lock_nonblocking(func):
    """Decorator on functions that require lock to be free. If the lock is not free it
       does not execute func."""
    def wrapper(*args, **kwargs):
        if lock.acquire(0): # zero argument means nonblocking
            func(*args, **kwargs)
            lock.release()
    return wrapper


class genericPage(object):
    """Defines the basic page object and the methods it should have."""

    def receive_signal(self, signal):
        print("method receive_signal not defined")

    @check_lock_nonblocking
    def display(self):
        print("method display not defined")

    @check_lock_blocking
    def change_page(self, new_page, *args, **kwargs):
        global page
        page = new_page(*args, **kwargs)
        print("page changed to {0}".format(page))

    @check_lock_blocking
    def change_state(self, new_state):
        print("changing state from {} to {}".format(self.state, new_state))
        self.state = new_state


class mainPage(genericPage):
    """Object that represents the main page, which shows general system
       information."""

    def __init__(self):
        pass

    def __str__(self):
        return "mainPage"

    def receive_signal(self, signum):
        if signum == signal.SIGUSR1:
            print("K1 pressed")
            pass
        elif signum == signal.SIGUSR2:
            print("K2 pressed")
            self.change_page(testPage)
        elif signum == signal.SIGALRM:
            print("K3 pressed")
            self.change_page(shutdownPage)

    @check_lock_nonblocking
    def display(self):
        self._update_data()
        text = "IP: {0}".format(self.ip_addr)
        draw.text((1, 1), text, font=font10b, fill=255)
        text = "Time: {0}".format(self.time)
        draw.text((1, 13), text,  font=font10b, fill=255)
        text = "ip"
        draw.text((4, 51), text, font=font10b, fill=255)
        text = "test"
        draw.text((51, 51), text, font=font10b, fill=255)
        text = "sd"
        draw.text((111, 51), text, font=font10b, fill=255)
        oled.drawImage(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

    def _update_data(self):
        self.ip_addr = get_ip()
        self.time = datetime.datetime.now().strftime("%H:%M:%S")


class testPage(genericPage):
    """Represents the test page, which is responsible for running tests."""

    def __init__(self):
        self.state = 0
        self.down = "waiting..."
        self.up = "waiting..."
        self.jitter = "waiting..."

    def __str__(self):
        return "testPage"

    def receive_signal(self, signum):
        if signum == signal.SIGUSR1:
            print("K1 pressed")
            if self.state == 0:
                self.change_state(1)
                self.thread = threading.Thread(target=self._start_test)
                self.thread.start()
            elif self.state == 1:
                pass
            elif self.state == 2:
                self.change_page(mainPage)
        elif signum == signal.SIGUSR2:
            print("K2 pressed")
            if self.state == 0:
                pass
            elif self.state == 1:
                pass
            elif self.state == 2:
                self.change_page(testPage)
        elif signum == signal.SIGALRM:
            print("K3 pressed")
            if self.state == 0:
                self.change_page(mainPage)
            elif self.state == 1:
                pass
            elif self.state == 2:
                self.change_page(shutdownPage)

    def _start_test(self):
        # conduct down test
        regex = re.compile('([0-9]+) Mbits/sec')
        cmd = "stdbuf -oL iperf3 -c 192.168.1.64 -R"
        process = Popen(cmd, shell=True, stdin=None, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                match = regex.search(line)
                if match is not None:
                    self.down = match.group(1) + " Mbit/s"
        process.wait()
        # conduct up test
        regex = re.compile('([0-9]+) Mbits/s')
        cmd = "stdbuf -oL iperf3 -c 192.168.1.64"
        process = Popen(cmd, shell=True, stdin=None, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                match = regex.search(line)
                if match is not None:
                    self.up = match.group(1) + " Mbit/s"
        process.wait()
        # conduct jitter test
        regex = re.compile(r'\s([0-9]+(\.[0-9]+)?) ms')
        cmd = "stdbuf -oL iperf3 -c 192.168.1.64 -u -R"
        process = Popen(cmd, shell=True, stdin=None, stdout=PIPE, stderr=STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                match = regex.search(line)
                if match is not None:
                    self.jitter = match.group(1) + " ms"
        process.wait()
        # change to state 2
        self.change_state(2)

    @check_lock_nonblocking
    def display(self):
        if self.state == 0: # ask user if they want to begin test
            text = "Begin test?"
            draw.text((1, 21), text,  font=font14b, fill=255)
            text = "yes"
            draw.text((4, 51), text,  font=font10b, fill=255)
            text = "no"
            draw.text((111, 51), text,  font=font10b, fill=255)
            oled.drawImage(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
        elif self.state == 1: # testing
            text = "down: {0}".format(self.down)
            draw.text((1, 1), text,  font=font10b, fill=255)
            text = "up: {0}".format(self.up)
            draw.text((1, 13), text,  font=font10b, fill=255)
            text = "jitter: {0}".format(self.jitter)
            draw.text((1, 25), text,  font=font10b, fill=255)
            oled.drawImage(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
        elif self.state == 2: # test either stopped or finished
            text = "down: {0}".format(self.down)
            draw.text((1, 1), text,  font=font10b, fill=255)
            text = "up: {0}".format(self.up)
            draw.text((1, 13), text,  font=font10b, fill=255)
            text = "jitter: {0}".format(self.jitter)
            draw.text((1, 25), text,  font=font10b, fill=255)
            text = "ip"
            draw.text((4, 51), text,  font=font10b, fill=255)
            text = "test"
            draw.text((51, 51), text,  font=font10b, fill=255)
            text = "sd"
            draw.text((111, 51), text,  font=font10b, fill=255)
            oled.drawImage(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

#    def testPage(self):
#        """Performs iperf test and displays results"""
#        # display 'testing down...'
#        text = "Testing down..."
#        draw.text((self.padding, self.padding+20), text,  font=font14b, fill=255)
#        oled.drawImage(image)
#        draw.rectangle((0, 0, width, height), outline=0, fill=0)
#        # do down test
#        down_client = iperf3.Client()
#        down_client.duration = self.iperf_duration
#        down_client.server_hostname = self.iperf_server
#        down_client.reverse = True
#        result = down_client.run()
#        #down = int(round(result.sent_Mbps))
#        down = result.sent_Mbps
#        # display 'testing up'
#        text = "Testing up..."
#        draw.text((self.padding, self.padding+20), text,  font=font14b, fill=255)
#        oled.drawImage(image)
#        draw.rectangle((0, 0, width, height), outline=0, fill=0)
#        # do up test
#        up_client = iperf3.Client()
#        up_client.duration = self.iperf_duration
#        up_client.server_hostname = self.iperf_server
#        up_client.reverse = False
#        result = up_client.run()
#        #up = int(round(result.sent_Mbps))
#        up = result.sent_Mbps
#        # display 'testing jitter'
#        text = "Testing jitter..."
#        draw.text((self.padding, self.padding+20), text,  font=font14b, fill=255)
#        oled.drawImage(image)
#        draw.rectangle((0, 0, width, height), outline=0, fill=0)
#        # do jitter test
#        j_client = iperf3.Client()
#        j_client.duration = self.iperf_duration
#        j_client.server_hostname = self.iperf_server
#        j_client.reverse = False
#        j_client.protocol = 'udp'
#        result = j_client.run()
#        jitter = result.jitter_ms
#        # display results


class shutdownPage(genericPage):
    """Represents the shutdown page, which takes care of shutting the
       system down."""

    def __init__(self):
        pass

    def __str__(self):
        return "shutdownPage"

    def receive_signal(self, signum):
        if signum == signal.SIGUSR1:
            print("K1 pressed")
            self._shut_down()
        elif signum == signal.SIGUSR2:
            print("K2 pressed")
            pass
        elif signum == signal.SIGALRM:
            print("K3 pressed")
            self.change_page(mainPage)

    @check_lock_nonblocking
    def display(self):
        text = "Shut down?"
        draw.text((21, 19), text,  font=font14b, fill=255)
        text = "yes"
        draw.text((4, 51), text,  font=font10b, fill=255)
        text = "no"
        draw.text((111, 51), text,  font=font10b, fill=255)
        oled.drawImage(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

    def _shut_down(self):
        """Actual shut down page"""
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        oled.drawImage(image)
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


def periodic_display():
    while True:
        page.display()
        time.sleep(0.1)


def receiveSignal(signum, stack):
    """Called whenever a signal is received."""
    thread = threading.Thread(target=page.receive_signal, args=[signum])
    thread.start()


if __name__ == "__main__":

    # initialization of "globals"
    width = 128
    height = 64
    padding = 1
    iperf_duration = 10
    iperf_server = '192.168.1.72'
    lock = thread.allocate_lock()
    print("constants initialized")

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
    print("oled initialized")
    page = mainPage()
    display_thread = threading.Thread(target=periodic_display)
    display_thread.start()
    print("display thread started")

    # assign receiveSignal to be called when buttons are pressed
    signal.signal(signal.SIGUSR1, receiveSignal) # button 1 (left)
    signal.signal(signal.SIGUSR2, receiveSignal) # button 2 (middle)
    signal.signal(signal.SIGALRM, receiveSignal) # button 3 (right)
    print("signals registered")

    while True:
        signal.pause()
