#!/usr/bin/env python3
import os
import numpy as np
import cv2
import math
from PIL import Image

def disp_scaled(name, image, delay=0):
    cv2.imshow(name, cv2.resize(image, None, fx=0.35, fy=0.35, interpolation = cv2.INTER_AREA))
    key = cv2.waitKey(delay)
    while key != 113 and delay == 0: # q
        key = cv2.waitKey(0)
        print(key)

def process_img(fname, imnum=0):
    imgc = cv2.imread(fname)
    img = cv2.cvtColor(imgc, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    kernel = np.ones((20,20), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    disp_scaled("morph", closed)
    print(cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE))

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cutoff = 1000
    out = []
    moments = []
    for c in contours:

        if cutoff < cv2.contourArea(c):
            out.append(c)
            moments.append(cv2.moments(c))

    contours = np.asarray(out)
    print(f'Found {len(contours)} contours')
    cv2.drawContours(imgc, contours, -1, (148, 0, 211), 13)
    #disp_scaled('image', imgc)

    for contour in contours:
        contour = contour[:,0,:]
        # get the corners of the card
        pts =  [[contour[:,0].min(), contour[:,1].min()],
                [contour[:,0].min(), contour[:,1].max()],
                [contour[:,0].max(), contour[:,1].max()],
                [contour[:,0].max(), contour[:,1].min()]]
        pts = np.asarray(pts)
        # draw the corners
        for pt in pts:
            cv2.circle(imgc, tuple(pt), 30, (0, 0, 255), 9)
        disp_scaled('image', imgc)

        # get the side lengths of the card so that we can calculate output image size
        def idist(p1, p2):
            return int(math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
        sidelens = [idist(pts[0], pts[1]), idist(pts[1], pts[2]),
                    idist(pts[2], pts[3]), idist(pts[3], pts[0])]
        sidelens.sort()
        height, width = sidelens[3], sidelens[3] * 3 / 5

        #box = np.asarray([(0, rect[1][1]), (0, 0), (rect[1][0], 0), (rect[1][0], rect[1][1])], dtype=np.float32)
        transform = cv2.findHomography(pts, box)
        print(transform[0])
        card = cv2.warpPerspective(imgc, transform[0], tuple(map(int, rect[1])), flags=cv2.INTER_LINEAR)
        rots = {0: card, 1: cv2.rotate(card, cv2.ROTATE_90_CLOCKWISE),
                2: cv2.rotate(card, cv2.ROTATE_180), 3: cv2.rotate(card, cv2.ROTATE_90_COUNTERCLOCKWISE)}
        key = 0
        rotation = 0
        #while key != 10: # enter in opencv3
        while key != 13: # enter in opencv4
            print(key)
            disp_scaled(f'card {imnum}', card, 1)
            key = cv2.waitKey(0)
            rotation = (rotation + 1) % 4
            card = rots[rotation]
        cv2.imwrite(os.path.join(OUTPUT_DIR, f'{OUTPUT_PREFIX}{imnum}{OUTPUT_FORMAT}'), card)
        cv2.destroyAllWindows()
        imnum += 1
    return imnum

INPUT_DIR = 'scanned'
OUTPUT_DIR = 'cards'
OUTPUT_PREFIX = 'card_'
OUTPUT_FORMAT = '.png'

process_img('homo1.jpg')

#n = 0
#for img in sorted(os.listdir(INPUT_DIR)):
#    print(img)
#    n = process_img(os.path.join(INPUT_DIR, img), n)
