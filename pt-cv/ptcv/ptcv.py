import time
import cv2
import numpy as np
import logging
import base64

LOG = logging.getLogger(__name__)


# a = time.time()
# b = time.time()
# latency = b - a
# print "Latency: %sms\n" % latency*1000

class Ptcv(object):
    def __init__(self):
        self.cap = None
        self.cap2 = None
        # __doc__ createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=true) -> retval
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        self.lastX = None
        self.lastY = None
        # self.imgScribble = None
        self.imgScribble = np.zeros((480,640,3), dtype = "uint8")

    def open_video(self):
        self.cap = cv2.VideoCapture(0)

    def open_video2(self):
        self.cap2 = cv2.VideoCapture(1)

    def grab(self):
        self.cap.grab()

    def grab2(self):
        self.cap2.grab()

    def retrieve(self):
        ret, img = self.cap.retrieve()
        return img

    def retrieve2(self):
        ret, img = self.cap2.retrieve()
        return img

    def retrieve_bw(self):
        ret, img = self.cap.retrieve()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def imshow_string(self, img, size, color=True):
        img = np.fromstring(img, dtype=np.uint8)
        if color == True:
            img = img.reshape(size[1], size[0], 3)
        else:
            img = img.reshape(size[1], size[0])
        self.imshow(img)

    def imshow(self, imgs):
        if type(imgs) != list:
            cv2.imshow('img', imgs)
            k = cv2.waitKey(1) & 0xff
            return

        # assume we have array type
        for i, img in enumerate(imgs):
            cv2.imshow('img%s'%i, img)
            k = cv2.waitKey(1) & 0xff

    def destroyAllWindows(self):
        cv2.destroyAllWindows()

    def resize(self, img, size):
        resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        return resized

    def circle(self, img, center, radius=10, color=(0, 0,255),
                   thickness=-1, lineType=8):
        # Line Types:
        # 8 (or omitted) - 8-connected line.
        # 4 - 4-connected line.
        # CV_AA - antialiased line.
        cv2.circle(img, center, radius, color, thickness, lineType)

    def putText(self, img, text, pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1, color=(0, 0,255), thickness=10, lineType=8):
        pos = (pos[0] + 20, pos[1] + 10)
        cv2.putText(img, text, pos, fontFace, fontScale, thickness)

    def remove_background(self, img):
        # Adapted from http://docs.opencv.org/trunk/doc/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html#py-background-subtraction
        return self.fgbg.apply(img)

    def open(self, img):
        # removes noise and fills holes
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(6,6))
        kernel = np.ones((3,3),np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
        return img

    def close(self, img):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(6,6))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=10)

    def adaptive_threshold(self, img):
        # http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html
        img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
        return img

    def to_bw(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def otsu_thresholding(self, img):
        # Otsu's thresholding after Gaussian filtering
        # http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html
        blur = cv2.GaussianBlur(img,(5,5),0)
        ret, img = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return img

    def blur(self, img):
        return cv2.GaussianBlur(img,(5,5),0)

    def attempt1(self, img):
        # result: super blocky!!!
        # inspiration http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_watershed/py_watershed.html
        img =  self.fgbg.apply(img)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=2)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=2)
        return img

    def attempt2(self, img):
        # result: Less blocky version of attempt1
        # remove background
        # fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=250, detectShadows=False)
        # ^ doesn't work, needs to be self.fgbg ... only one instance allowed
        img =  self.fgbg.apply(img)
        # remove noise
        kernel = np.ones((3,3),np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
        return img

    def attempt3(self, img_arr):
        # result: super psychodelic!
        # inspiration: https://blog.cedric.ws/opencv-simple-motion-detection
        d1 = abs(img_arr[0] - img_arr[2])
        d2 = abs(img_arr[1] - img_arr[2])
        result = np.bitwise_and(d1, d2)
        ret, thresh = cv2.threshold(result,35,255,cv2.THRESH_BINARY)
        return thresh

    def attempt4(self, img_arr):
        # result:
        # inspiration: http://docs.opencv.org/trunk/modules/video/doc/motion_analysis_and_object_tracking.html
        pass

    def detect_rgb_color(self, img):
        # list of color upper and lower rgb boundaries
        boundaries = [
            ([17, 15, 100], [50, 56, 200]),
            ([86, 31, 4], [220, 88, 50]),
            ([25, 146, 190], [62, 174, 250]),
            ([103, 86, 65], [145, 133, 128])
        ]

        # loop over the boundaries
        for (lower, upper) in boundaries:
            # create NumPy arrays from the boundaries
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
         
            # find the colors within the specified boundaries and apply
            # the mask
            mask = cv2.inRange(img, lower, upper)
            output = cv2.bitwise_and(img, img, mask = mask)
         
            # show the imgs
            cv2.imshow("imgs", np.hstack([img, output]))
            cv2.waitKey(0)

    def trace_moments(self, img):
        # Moments
        moment = cv2.moments(img)
        moment10 = moment['m10']
        moment01 = moment['m01']
        area = moment['m00']

        # locations
        if area <= 0:
            "returning early"
            return self.imgScribble, None

        posX = int(moment10/area)
        posY = int(moment01/area)

        if self.lastX == None:
            self.lastX = posX
        if self.lastY == None:
            self.lastY = posY

        # print "position (%d,%d)" % (posX, posY)

        # Draw a line only if its a valid position
        # if self.lastX > 0 and self.lastY > 0 and posX > 0 and posY > 0:
            # Draw a yellow line from the previous point to the current point
        current_pos = (int(posX), int(posY))
        last_pos = (int(self.lastX), int(self.lastY))
        color = (0,255,255)
        cv2.line(self.imgScribble, current_pos, last_pos, color, 5)

        self.lastX = posX
        self.lastY = posY

        return self.imgScribble, (posX, posY)

    def get_p1loc(self, img):
        imghsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsvimg = cv2.inRange(imghsv, (40, 100, 100), (90, 255, 255)) # lime greene
        hsvimg = self.open(hsvimg)
        imgScribble, loc = self.trace_moments(hsvimg)
        # self.imshow([hsvimg, imgScribble, img])
        return loc

    def get_p2loc(self, img):
        imghsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsvimg = cv2.inRange(imghsv, (100, 100, 100), (105, 255, 255)) # orange
        hsvimg = self.open(hsvimg)
        imgScribble, loc = self.trace_moments(hsvimg)
        # self.imshow([hsvimg, imgScribble, img])
        return loc

    def get_p3loc(self, img):
        imghsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsvimg = cv2.inRange(imghsv, (20, 100, 100), (30, 255, 255)) # sky blue
        hsvimg = self.open(hsvimg)
        imgScribble, loc = self.trace_moments(hsvimg)
        # self.imshow([hsvimg, imgScribble, img])
        return loc

    def get_p4loc(self, img):
        imghsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsvimg = cv2.inRange(imghsv, (120, 100, 100), (140, 255, 255)) # red
        hsvimg = self.open(hsvimg)
        imgScribble, loc = self.trace_moments(hsvimg)
        # self.imshow([imgScribble, img, hsvimg])
        return loc

    def np_to_jpeg_base64(self, img):
        # http://docs.opencv.org/modules/highgui/doc/reading_and_writing_images_and_video.html#imencode
        # also try PGM
        # http://en.wikipedia.org/wiki/Netpbm_format
        ret, data = cv2.imencode('.jpeg', img, [cv2.IMWRITE_JPEG_QUALITY, 50])
        jpeg_base64 = base64.b64encode(data.tostring())
        # return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
        return "data:image/jpeg;base64,%s" % jpeg_base64

    def str_to_npframe(str_frame, x=640, y=480, z=3):
        np_frame = np.fromstring(str_frame, dtype=np.uint8)
        np_frame = np_frame.reshape(x,y,z)
        return np_frame

# # key terms:
# findContour
# regionFill
# grabcut and watershed are manually marked segementation
