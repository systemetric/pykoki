#!/usr/bin/env python

from __future__ import print_function

import cv
import sys

from pykoki import PyKoki, Point2Di, Point2Df, CameraParams

if len(sys.argv) != 2:
    print("opencv_example.py IMG_FILE", file=sys.stderr)
    exit(1)

filename = sys.argv[1]

img = cv.LoadImage( filename, cv.CV_LOAD_IMAGE_GRAYSCALE )
assert img, "Failed to load image at {0}".format(filename)

koki = PyKoki()

params = CameraParams(Point2Df( img.width/2, img.height/2 ),
                      Point2Df(571, 571),
                      Point2Di( img.width, img.height ))

print(koki.find_markers( img, 0.1, params ))
