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
    
    def __init__(self, K1_action=None, K2_action=None, K3_action=None):
        self.width = 128
        self.height = 64
        self.padding = 1
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font10b = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10)
        self.font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
        self.font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14)
        self.fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14)
        self.fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24)
        oled.init()
        oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
        oled.setHorizontalMode()
        self.telusSlogan()
        if K1_action is None:
            K1_action = self.defaultAction
        if K2_action is None:
            K2_action = self.defaultAction
        if K3_action is None:
            K3_action = self.defaultAction
        signal.signal(signal.SIGUSR1, K1_action) # button 1 (left)
        signal.signal(signal.SIGUSR2, K2_action) # button 2 (middle)
        signal.signal(signal.SIGALRM, K3_action) # button 3 (right)

    def drawPage(self, text_array):
        if len(text_array) == 1:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
        if len(text_array) == 2:
            self.draw.text((self.padding, self.padding), text_array[0],  font=self.font10b, fill=255)
            self.draw.text((self.padding, self.padding+12), text_array[1], font=self.font10b, fill=255)
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
        # clear current image
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def defaultAction(self, signum, stack):
        self.drawPage(["Action not defined"])
        time.sleep(2)
        self.telusSlogan()

    def telusSlogan(self):
        self.draw.text((self.padding+26, self.padding), "TELUS", font=self.fontb24, fill=255)
        self.draw.text((self.padding+22, self.padding+30), "The Future", font=self.font14, fill=255)
        self.draw.text((self.padding+19, self.padding+44), "is Friendly", font=self.font14, fill=255)
        oled.drawImage(self.image)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)


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
        

#
#def draw_page():
#    
#    # Draw current page indicator
#    if showPageIndicator:
#        dotWidth=4
#        dotPadding=2
#        dotX=width-dotWidth-1
#        dotTop=(height-pageCount*dotWidth-(pageCount-1)*dotPadding)/2
#        for i in range(pageCount):
#            if i==page_index:
#                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=255)
#            else:
#                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=0)
#            dotTop=dotTop+dotWidth+dotPadding
#
#    if page_index==0:
#        text = time.strftime("%A")
#        draw.text((2,2),text,font=font14,fill=255)
#        text = time.strftime("%e %b %Y")
#        draw.text((2,18),text,font=font14,fill=255)
#        text = time.strftime("%X")
#        draw.text((2,40),text,font=fontb24,fill=255)
#    elif page_index==1:
#        # Draw some shapes.
#        # First define some constants to allow easy resizing of shapes.
#        padding = 2
#        top = padding
#        bottom = height-padding
#        # Move left to right keeping track of the current x position for drawing shapes.
#        x = 0
#	IPAddress = get_ip()
#        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
#        CPU = subprocess.check_output(cmd, shell = True )
#        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
#        MemUsage = subprocess.check_output(cmd, shell = True )
#        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
#        Disk = subprocess.check_output(cmd, shell = True )
#        tempI = int(open('/sys/class/thermal/thermal_zone0/temp').read());
#        if tempI>1000:
#            tempI = tempI/1000
#        tempStr = "CPU TEMP: %sC" % str(tempI)
#
#        draw.text((x, top+5),       "IP: " + str(IPAddress),  font=smartFont, fill=255)
#        draw.text((x, top+5+12),    str(CPU), font=smartFont, fill=255)
#        draw.text((x, top+5+24),    str(MemUsage),  font=smartFont, fill=255)
#        draw.text((x, top+5+36),    str(Disk),  font=smartFont, fill=255)
#        draw.text((x, top+5+48),    tempStr,  font=smartFont, fill=255)
#    elif page_index==3: #shutdown -- no
#        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)
#
#        draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
#        draw.text((4, 22),  'Yes',  font=font11, fill=255)
#
#        draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
#        draw.text((4, 40),  'No',  font=font11, fill=0)
#
#    elif page_index==4: #shutdown -- yes
#        draw.text((2, 2),  'Shutdown?',  font=fontb14, fill=255)
#
#        draw.rectangle((2,20,width-4,20+16), outline=0, fill=255)
#        draw.text((4, 22),  'Yes',  font=font11, fill=0)
#
#        draw.rectangle((2,38,width-4,38+16), outline=0, fill=0)
#        draw.text((4, 40),  'No',  font=font11, fill=255)
#
#    elif page_index==5:
#        draw.text((2, 2),  'Shutting down',  font=fontb14, fill=255)
#        draw.text((2, 20),  'Please wait',  font=font11, fill=255)
#
#    oled.drawImage(image)
#
#    lock.acquire()
#    drawing = False
#    lock.release()
#
#
#image0 = Image.open('friendllyelec.png').convert('1')
#oled.drawImage(image0)
#time.sleep(2)
#
#
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
    signal.pause()
