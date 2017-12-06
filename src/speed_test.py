#!/usr/bin/env python
#
#

import bakebit_128_64_oled as oled
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
import sys
import subprocess
import threading
import signal
import os
import socket


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


class NanoHatOled(object):
    
    def __init__(self):
        self.width = 128
        self.height = 64
        oled.init()
        oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
        oled.setHorizontalMode()
        # make signals
        signal.signal(signal.SIGUSR1, self.receive_signal) # button 1 (left)
        signal.signal(signal.SIGUSR2, self.receive_signal) # button 2 (middle)
        signal.signal(signal.SIGALRM, self.receive_signal) # button 3 (right)

    def draw_page(self):
        # one line
        # two lines
        # three lines
        # four lines
        # five lines

    def receive_signal(self, signum, stack):
        global pageIndex

        lock.acquire()
        page_index = pageIndex
        lock.release()

        if page_index==5:
            return

        if signum == signal.SIGUSR1:
            print 'K1 pressed'
            if is_showing_power_msgbox():
                if page_index==3:
                    update_page_index(4)
                else:
                    update_page_index(3)
                draw_page()
            else:
                pageIndex=0
                draw_page()

        if signum == signal.SIGUSR2:
            print 'K2 pressed'
            if is_showing_power_msgbox():
                if page_index==4:
                    update_page_index(5)
                    draw_page()
     
                else:
                    update_page_index(0)
                    draw_page()
            else:
                update_page_index(1)
                draw_page()

        if signum == signal.SIGALRM:
            print 'K3 pressed'
            if is_showing_power_msgbox():
                update_page_index(0)
                draw_page()
            else:
                update_page_index(3)
                draw_page()


#pageCount=2
#pageIndex=0
#showPageIndicator=False
#
#drawing = False
#
#image = Image.new('1', (width, height))
#draw = ImageDraw.Draw(image)
#fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24);
#font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14);
#smartFont = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10);
#fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14);
#font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11);
#
## get rid of this
#lock = threading.Lock()
#
#def draw_page():
#    global drawing
#    global image
#    global draw
#    global oled
#    global font
#    global font14
#    global smartFont
#    global width
#    global height
#    global pageCount
#    global pageIndex
#    global showPageIndicator
#    global width
#    global height
#    global lock
#
#    lock.acquire()
#    is_drawing = drawing
#    page_index = pageIndex
#    lock.release()
#
#    if is_drawing:
#        return
#
#    lock.acquire()
#    drawing = True
#    lock.release()
#    
#    # Draw a black filled box to clear the image.            
#    draw.rectangle((0,0,width,height), outline=0, fill=0)
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
#def is_showing_power_msgbox():
#    global pageIndex
#    lock.acquire()
#    page_index = pageIndex
#    lock.release()
#    if page_index==3 or page_index==4:
#        return True
#    return False
#
#
#def update_page_index(pi):
#    global pageIndex
#    lock.acquire()
#    pageIndex = pi
#    lock.release()
#
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
    print("Name is main.")
