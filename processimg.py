#!/usr/bin/env python3
import numpy as np
import cv2
from PIL import Image

def disp_scaled(name, image, delay=0):
    cv2.imshow(name, cv2.resize(image, None, fx=0.15, fy=0.15, interpolation = cv2.INTER_AREA))
    key = cv2.waitKey(0)
    while key != 113: # q
        key = cv2.waitKey(0)
        print(key)

fil = "img1.jpg"
imgc = cv2.imread(fil)
img = cv2.cvtColor(imgc, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
kernel = np.ones((20,20), np.uint8)
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
#disp_scaled("morph", closed)

im, contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

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
disp_scaled('image', imgc)

for contour in [contours[2]]:
    contour = contour[:,0,:]
    rect = cv2.minAreaRect(contour)
    print(rect)
    cv2.circle(imgc, tuple(map(int, rect[0])), 30, (0, 0, 255), 9)
    cv2.circle(imgc, tuple(map(int, (rect[0][0] + rect[1][0]/2, rect[0][1] + rect[1][1]/2))), 30, (0, 0, 255), 9)
    cv2.circle(imgc, tuple(map(int, (rect[0][0] + rect[1][0]/2, rect[0][1] - rect[1][1]/2))), 30, (0, 0, 255), 9)
    cv2.circle(imgc, tuple(map(int, (rect[0][0] - rect[1][0]/2, rect[0][1] + rect[1][1]/2))), 30, (0, 0, 255), 9)
    cv2.circle(imgc, tuple(map(int, (rect[0][0] - rect[1][0]/2, rect[0][1] - rect[1][1]/2))), 30, (0, 0, 255), 9)
    rotation = cv2.getRotationMatrix2D(rect[0], rect[2], 1.0)
    translation = np.asarray([[1, 0, -rect[0][0] + rect[1][0]/2],
                              [0, 1, -rect[0][1] + rect[1][1]/2],
                              [0, 0, 1]], dtype=np.float32)
    #rotated = cv2.warpAffine(imgc, rotation @ translation, imgc.shape[:2][::-1], flags=cv2.INTER_LINEAR)
    rotated = cv2.warpAffine(imgc, rotation @ translation, tuple(map(int, rect[1])), flags=cv2.INTER_LINEAR)
    disp_scaled('card', rotated)

disp_scaled('image', imgc)
