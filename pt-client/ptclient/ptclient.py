#!/usr/bin/python
import sys
import time
import tornado.websocket
import pickle
import time

from tornado import gen
from tornado.websocket import websocket_connect

from pt import pt
from ptcv import ptcv
from pt.common import getLogger

from picamera.array import PiRGBArray
from picamera import PiCamera



resolution = 1
res_x = int(640*1)
res_y = int(480*1)

# res_x = 1440
# res_y = 1080

# res_x = 1920
# res_y = 1080

x = 0
y = 0

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera) # stills
camera.resolution = (res_x, res_y)
camera.rotation = 180

camera.framerate = 32
camera.contrast = 5
camera.brightness = 60
camera.saturation = 10
camera.ISO = 800
rawCapture = PiRGBArray(camera, size=(res_x, res_y))

# allow the camera to warmup
time.sleep(0.1)


description = 'pt-client sends camera frames the central pt server'
log = getLogger("pt-client", description, level="debug")


class ZoneStream(object):
    def __init__(self):
        self.ptcv = ptcv.Ptcv()

    @gen.coroutine
    def initialize_connections(self):
        zone_id = 0
        url = "ws://192.168.0.104:8888/zone/video/%s" % zone_id
        self.ws_video = yield websocket_connect(url)
        log.info("Connected to pt-server at %s" % url)
        self.ptcv.open_video()

    @gen.coroutine
    def stream_video(self):
        log.info("Streaming video...")
        count = 0
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            count = count + 1
            grabtime = time.time()
            img = frame.array
            self.send_frame(img, grabtime, count)

    @gen.coroutine
    def send_frame(self, img, grabtime, count):
            jpeg_base64 = self.ptcv.np_to_jpeg_base64(img)

            img_dict = {
                'time': grabtime,
                'frame': jpeg_base64,
                'frame_id': count,
                'zone_id': "%s,%s" % (x, y),
                'zone_x': x,
                'zone_y': y,
                'players': None
            }
            pickled_dict = pickle.dumps(img_dict)
            self.ws_video.write_message(pickled_dict)

            rawCapture.truncate(0)



@gen.coroutine
def main():
    zstream = ZoneStream()
    yield zstream.initialize_connections()
    yield zstream.stream_video()

if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.run_sync(main)