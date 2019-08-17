#!/usr/bin/python3
import cv2
import os
import argparse


disp_scale = 0.5


def disp_scaled(name, image, delay=0):
    global disp_scale
    #cv2.imshow(name, cv2.resize(image, None, fx=0.95, fy=0.95, interpolation = cv2.INTER_AREA))
    cv2.imshow(name, cv2.resize(image, None, fx=disp_scale, fy=disp_scale, interpolation = cv2.INTER_AREA))
    key = cv2.waitKey(delay)
    while key != 113 and delay == 0: # q
        key = cv2.waitKey(0)
        print(key)


def correct(img, quiet=False):
    disp_scaled('img', img, delay=1)
    balancer = cv2.xphoto.createSimpleWB()
    i2 = balancer.balanceWhite(img)
    disp_scaled('simple', i2, delay=1)

    gray = cv2.cvtColor(i2, cv2.COLOR_BGR2GRAY)

    block_size = 5
    c = 2
    thresh_val = 127
    erosion = 2
    blur = 5

    def update_images():
        nonlocal gray, block_size, c, thresh_val, erosion, blur
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (erosion, erosion))
        _, i3 = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY) # create thresh window
        i3 = cv2.erode(i3, erode_kernel)
        i3 = cv2.GaussianBlur(i3, (blur, blur), 0)
        disp_scaled('thresh', i3, 1)
        i4 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
        i4 = cv2.erode(i4, erode_kernel)
        i4 = cv2.GaussianBlur(i4, (blur, blur), 0)
        disp_scaled('athresh', i4, 1)

    def on_simple_thresh(val):
        nonlocal thresh_val
        thresh_val = val
        update_images()

    def on_block(val):
        nonlocal block_size
        if val % 2 == 1:
            block_size = val
            update_images()

    def on_c(val):
        nonlocal c
        c = val
        update_images()

    def on_erosion(val):
        nonlocal erosion
        erosion = val
        update_images()

    def on_blur(val):
        nonlocal blur
        if val % 2 == 1:
            blur = val
        update_images()

    update_images()
    cv2.createTrackbar('Threshold Value', 'thresh', 0, 255, on_simple_thresh)
    cv2.createTrackbar('Block Size', 'athresh', 1, 51, on_block)
    cv2.createTrackbar('C', 'athresh', 0, 255, on_c)
    cv2.createTrackbar('Blur Size', 'thresh', 0, 31, on_blur)
    cv2.createTrackbar('Erosion Size', 'thresh', 0, 500, on_erosion)
    while cv2.waitKey(0) != 113: #q
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='file or directory to process')
    parser.add_argument('-q', '--quiet', help='whether or not to show a gui and take user input', action='store_const', const=True, default=False)
    parser.add_argument('-s', '--scale', help='scale factor for shown images', type=float, default=0.5)

    args = parser.parse_args()
    print(args)

    i = cv2.imread(args.file)
    disp_scale = args.scale

    correct(i, args.quiet)
