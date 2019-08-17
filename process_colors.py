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
    balancers = [cv2.xphoto.createSimpleWB(),
                cv2.xphoto.createGrayworldWB(),
                cv2.xphoto.createLearningBasedWB()]

    balancer = 0
    block_size = 51
    c = 47
    thresh_val = 127
    erosion = 14
    blur = 29
    simple_thresh = None
    adaptive_thresh = None
    balanced = None
    gray = None

    def update_images():
        nonlocal balanced, balancer, gray, block_size, c, thresh_val, erosion, blur, simple_thresh, adaptive_thresh
        # do the white balance correction
        balanced = balancers[balancer].balanceWhite(img)
        disp_scaled('balanced', balanced, delay=1)
        gray = cv2.cvtColor(balanced, cv2.COLOR_BGR2GRAY)

        # prepare for image correction w/ simple threshold method
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (erosion, erosion))
        _, simple_thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY) # create thresh window
        simple_thresh = cv2.erode(simple_thresh, erode_kernel)
        simple_thresh = cv2.GaussianBlur(simple_thresh, (blur, blur), 0)
        disp_scaled('thresh', simple_thresh, 1)
        simple_thresh = cv2.add(cv2.cvtColor(simple_thresh, cv2.COLOR_GRAY2BGR), balanced)
        disp_scaled('thresh_card', simple_thresh, 1)

        # same image correction, but this time with adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
        adaptive_thresh = cv2.erode(adaptive_thresh, erode_kernel)
        adaptive_thresh = cv2.GaussianBlur(adaptive_thresh, (blur, blur), 0)
        disp_scaled('athresh', adaptive_thresh, 1)
        adaptive_thresh = cv2.add(cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR), balanced)
        disp_scaled('athresh_card', adaptive_thresh, 1)

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
    cv2.createTrackbar('Threshold Value', 'thresh', thresh_val, 255, on_simple_thresh)
    cv2.createTrackbar('Block Size', 'athresh', block_size, 151, on_block)
    cv2.createTrackbar('C', 'athresh', c, 255, on_c)
    cv2.createTrackbar('Blur Size', 'thresh', blur, 131, on_blur)
    cv2.createTrackbar('Erosion Size', 'thresh', erosion, 500, on_erosion)
    key = cv2.waitKey(0)
    while key != 113: #q
        if key == 113:
            print('wht')
        elif key == 115: # s
            cv2.imwrite('out_simple.png', simple_thresh)
            cv2.imwrite('out_adaptive.png', adaptive_thresh)
            print('wrote images')
        elif key == 112: # p
            print(f'block_size: {block_size}')
            print(f'c: {c}')
            print(f'thresh_val: {thresh_val}')
            print(f'erosion: {erosion}')
            print(f'blur: {blur}')
            d = {0: 'simple', 1: 'grayworld', 2: 'learning'}
            print(f'balancer: {d[balancer]}')
        elif key == 109:
            balancer = (balancer + 1) % 3
            d = {0: 'simple', 1: 'grayworld', 2: 'learning'}
            print(f'Now using {d[balancer]} balancer')
            update_images()
        else:
            print(f'Unknown key: {key}')
        key = cv2.waitKey(0)


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
