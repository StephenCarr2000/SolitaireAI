import cv2
import numpy as np
import pyautogui
import random
import time
import platform
import subprocess

is_retina = False
#if platform.system() == "Darwin":
#    is_retina = subprocess.call("system_profiler SPDisplaysDataType | grep 'retina'", shell=True)

'''

grabs a region (topx, topy, bottomx, bottomy)
to the tuple (topx, topy, width, height)

input : a tuple containing the 4 coordinates of the region to capture

output : a PIL image of the area selected.

'''


def region_grabber(region):
    if is_retina: region = [n * 2 for n in region]
    x1 = region[0]
    y1 = region[1]
    width = region[2] - x1
    height = region[3] - y1

    return pyautogui.screenshot(region=(x1, y1, width, height))


'''

Searchs for an image within an area

input :

image : path to the image file (see opencv imread for supported types)
x1 : top left x value
y1 : top left y value
x2 : bottom right x value
y2 : bottom right y value
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
im : a PIL image, usefull if you intend to search the same unchanging region for several elements

returns :
the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

'''


def imagesearcharea(image, x1, y1, x2, y2, precision=0.8, im=None):
    if im is None:
        im = region_grabber(region=(x1, y1, x2, y2))
        if is_retina:
            im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
        # im.save('testarea.png') usefull for debugging purposes, this will save the captured region as "testarea.png"

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    #res=cv2.matchTemplate(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), cv2.imread(image, cv2.IMREAD_COLOR),cv2.TM_CCORR_NORMED)
    #res = cv2.matchTemplate(img_gray, template, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


'''

click on the center of an image with a bit of random.
eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
Usefull to avoid anti-bot monitoring while staying precise.

this function doesn't search for the image, it's only ment for easy clicking on the images.

input :

image : path to the image file (see opencv imread for supported types)
pos : array containing the position of the top left corner of the image [x,y]
action : button of the mouse to activate : "left" "right" "middle", see pyautogui.click documentation for more info
time : time taken for the mouse to move from where it was to the new position
'''


def click_image(image, pos, action, timestamp, dclick,offset=5):
    img = cv2.imread(image)    
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    if dclick==True:
        dclick()
    else:
        sclick()

    #pyautogui.click(button=action)
    #pyautogui.doubleClick()

def sclick():
    pyautogui.mouseDown()
    pyautogui.mouseUp()

def dclick():
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    
'''
Searchs for an image on the screen

input :

image : path to the image file (see opencv imread for supported types)
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
im : a PIL image, usefull if you intend to search the same unchanging region for several elements

returns :
the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

'''


def imagesearch(image, precision=0.8):
    #print("is_retina: " + str(is_retina))
    im = pyautogui.screenshot()
    #im.save('testDebugImg1.png')
    if is_retina:
        im.thumbnail((round(im.size[0] * 0.5), round(im.size[1] * 0.5)))
    #im.save('testarea.png') # useful for debugging purposes, this will save the captured region as "testarea.png"
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    #np.set_printoptions(threshold=np.inf, precision=5, linewidth=np.inf)
    #f1 = open('test.bin','w')
    #f1.write(np.array2string(template))
    #f1.close()
    #print("printing template\n")
    #print(template)
    template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    #res=cv2.matchTemplate(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), cv2.imread(image, cv2.IMREAD_COLOR),cv2.TM_CCORR_NORMED)
    #res = cv2.matchTemplate(img_gray, template, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print("min_val:" + str(min_val) + ", max_val:" + str(max_val) + ",min_loc" + str(min_loc) + ",max_loc:" + str(max_loc))
    if max_val < precision:
        return [-1, -1]
    return max_loc


'''
Searchs for an image on screen continuously until it's found.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image 
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element if found as an array [x,y] 

'''


def imagesearch_loop(image, timesample, precision=0.8):
    pos = imagesearch(image, precision)
    while pos[0] == -1:
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
    return pos


'''
Searchs for an image on screen continuously until it's found or max number of samples reached.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image
maxSamples: maximum number of samples before function times out.
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element if found as an array [x,y] 

'''


def imagesearch_numLoop(image, timesample, maxSamples, precision=0.8):
    pos = imagesearch(image, precision)
    count = 0
    while pos[0] == -1:
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
        count = count + 1
        if count > maxSamples:
            break
    return pos


'''
Searchs for an image on a region of the screen continuously until it's found.

input :
image : path to the image file (see opencv imread for supported types)
time : Waiting time after failing to find the image 
x1 : top left x value
y1 : top left y value
x2 : bottom right x value
y2 : bottom right y value
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

returns :
the top left corner coordinates of the element as an array [x,y] 

'''


def imagesearch_region_loop(image, timesample, x1, y1, x2, y2, precision=0.8):
    pos = imagesearcharea(image, x1, y1, x2, y2, precision)

    while pos[0] == -1:
        time.sleep(timesample)
        pos = imagesearcharea(image, x1, y1, x2, y2, precision)
    return pos


'''
Searches for an image on the screen and counts the number of occurrences.

input :
image : path to the target image file (see opencv imread for supported types)
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

returns :
the number of times a given image appears on the screen.
optionally an output image with all the occurances boxed with a red outline.

'''


def imagesearch_count(image, x1, y1, x2, y2, precision=0.9):
    #img_rgb = pyautogui.screenshot()
    img_rgb = region_grabber(region=(x1, y1, x2, y2))
    img_rgb.save('testimg_copy.png')
    #if is_retina:
    #    img_rgb.thumbnail((round(img_rgb.size[0] * 0.5), round(img_rgb.size[1] * 0.5)))

    img_rgb = np.array(img_rgb)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    #res=cv2.matchTemplate(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), cv2.imread(image, cv2.IMREAD_COLOR),cv2.TM_CCORR_NORMED)
    #res = cv2.matchTemplate(img_gray, template, cv2.TM_CCORR_NORMED)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2) // Uncomment to draw boxes around found occurances
        count = count + 1
    # cv2.imwrite('result.png', img_rgb) // Uncomment to write output image with boxes drawn around occurances
    return count


def r(num, rand):
    return num + rand * random.random()

#def matchCall(img):
#        cv2.imread(image, 0)
#        return cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
