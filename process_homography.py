#!/usr/bin/env python3
import os
import numpy as np
import cv2
import math
from PIL import Image

def disp_scaled(name, image, delay=0):
    #cv2.imshow(name, cv2.resize(image, None, fx=0.95, fy=0.95, interpolation = cv2.INTER_AREA))
    cv2.imshow(name, cv2.resize(image, None, fx=0.65, fy=0.65, interpolation = cv2.INTER_AREA))
    key = cv2.waitKey(delay)
    while key != 113 and delay == 0: # q
        key = cv2.waitKey(0)
        print(key)

def process_img(fname, imnum=0):
    imgc = cv2.imread(fname)
    img = cv2.cvtColor(imgc, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)
    kernel = np.ones((20,20), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # disp_scaled("morph", closed)

    #contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cutoff = 1000000
    out = []
    moments = []
    for c in contours:

        if cv2.contourArea(c) > cutoff:
            out.append(c)
            moments.append(cv2.moments(c))

    contours = np.asarray(out)
    #print(f'Found {len(contours)} contours')
    if len(contours) != 1:
        raise ValueError(f'BAD N CONTOURS {fname}')
    # cv2.drawContours(imgc, contours, -1, (148, 0, 211), 13)
    # disp_scaled('image', imgc)

    for contour in contours:
        contour = contour[:,0,:]
        # get the corners of the card
        pts = cv2.approxPolyDP(contour, 50, True)[:,0,:]
        if len(pts) != 4:
            raise ValueError(f'BAD RECT {fname}')
        pts = pts[pts[:,1].argsort()]
        if pts[0][0] > pts[1][0]:
            tmp = tuple(pts[0])
            pts[0] = pts[1]
            pts[1] = tmp
        if pts[2][0] > pts[3][0]:
            tmp = tuple(pts[2])
            pts[2] = pts[3]
            pts[3] = tmp
        #print(pts)
        # draw the corners
        # for pt in pts:
        #     cv2.circle(imgc, tuple(pt), 30, (0, 0, 255), 9)
        # disp_scaled('image', imgc)

        # get the side lengths of the card so that we can calculate output image size
        def idist(p1, p2):
            return int(math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
        sidelens = [idist(pts[0], pts[1]), idist(pts[1], pts[2]),
                    idist(pts[2], pts[3]), idist(pts[3], pts[0])]
        sidelens.sort()
        height, width = sidelens[3], sidelens[3] * 3 / 5

        box = np.asarray([[0,0], [width, 0], [0, height], [width, height]])
        transform = cv2.findHomography(pts, box)
        card = cv2.warpPerspective(imgc, transform[0], (int(width), int(height)), flags=cv2.INTER_LINEAR)
        rots = {0: card, 1: cv2.rotate(card, cv2.ROTATE_90_CLOCKWISE),
                2: cv2.rotate(card, cv2.ROTATE_180), 3: cv2.rotate(card, cv2.ROTATE_90_COUNTERCLOCKWISE)}
        key = 0
        rotation = 0
        #while key != 10: # enter in opencv3
        # while key != 13: # enter in opencv4
            #print(key)
        disp_scaled(f'card', card, 16)
            #key = cv2.waitKey(16)
            #rotation = (rotation + 1) % 4
            #card = rots[rotation]
        cv2.imwrite(os.path.join(OUTPUT_DIR, f'{OUTPUT_PREFIX}{imnum}{OUTPUT_FORMAT}'), card)
        #cv2.destroyAllWindows()
        imnum += 1
    return imnum

INPUT_DIR = 'scanned'
OUTPUT_DIR = 'cards'
OUTPUT_PREFIX = 'club_card_'
OUTPUT_FORMAT = '.png'

n = 0
for img in sorted(os.listdir(INPUT_DIR)):
    if 'CR2' in img:
        continue
    #print(img)
    try:
        n = process_img(os.path.join(INPUT_DIR, img), n)
    except ValueError as e:
        print(e)
