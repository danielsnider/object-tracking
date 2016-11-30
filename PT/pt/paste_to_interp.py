#!/usr/bin/python

import cv2
import numpy as np

img = cv2.imread('gamemap.jpg')
p = cv2.pyrMeanShiftFiltering(img, 5, 10)
# p = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
# p = cv2.adaptiveThreshold(p,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
p = cv2.pyrMeanShiftFiltering(p, 50, 100)
cv2.imwrite("out.jpg", p)

cv2.imshow('img', img)
k = cv2.waitKey(0) & 0xff


cv2.destroyAllWindows()