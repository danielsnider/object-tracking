#!/usr/bin/python
import sys
import time
import pika
import json
import time
import pickle
import threading
import tornado.websocket
import signal
import os

from tornado import gen
from tornado.websocket import websocket_connect


import pt
import ptcv
from common import getLogger

# import code
# code.interact(local=locals())

description = 'pt-client sends camera frames the central pt server'
log = getLogger("pt-client", description, level="info")

# resolution = 3
res_x = 640
res_y = 480

# vid = "/Users/dan/Movies/bal2.h264"
vid = "/home/dan/mac/Movies/bal2.h264"

vidfile = True
webcam = False

send = True

# amqp_host = "192.168.111.154"
# pt_server = "192.168.111.76"
# localhost = "127.0.0.1"
# amqp_host = "172.16.6.2"
# pt_server = "192.168.0.105"
amqp_host = "ptserver.local"
pt_server = "ptserver.local"


try:
    from picamera.array import PiRGBArray
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError as e:
    raspberry_pi = False
else:
    raspberry_pi = True

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
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

io_loop = tornado.ioloop.IOLoop.instance()

class ZoneStream(object):
    def __init__(self):
        self.ptcv = ptcv.Ptcv()
        self.count = 0
        # Browser settings
        self.stream1 = "final"
        self.stream2 = "original"
        self.stream1quality = 25
        self.stream2quality = 15

        # OpenCV settings
        #
        # Background subtraction
        self.bg_threshold = 16
        self.bg_history = 500
        self.bg_detectshadows = False

        # Noise reduction
        self.open_kernel = (3,3)
        self.open_iterations = 2
        self.erode_kernel = (3,3)
        self.erode_iterations = 2

        # Find Contours
        self.min_size = 50
        self.max_size = 500

        # Tracking Algorithm
        self.max_jump_dist = 200
        self.initial_confidence = 1
        self.confidence_increase = 1
        self.confidence_reduction = 1
        self.confidence_threshold = -100
        self.min_confidence = -100
        self.max_confidence = 100

        self.amqp_thread = threading.Thread(target=self.amqp_consumer, args=())
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=amqp_host))
        self.amqp_thread.daemon = True
        self.amqp_thread.start()

    def amqp_consumer(self):
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='clients',
                                queue=queue_name)
        self.channel.basic_consume(self.amqp_message_handler,
                                    queue=queue_name,
                                    no_ack=True)

        log.info("Listening for amqp messages.")
        self.channel.start_consuming()

    def amqp_message_handler(self, ch, method, properties, body):
        # log.info("ch: %s" % ch)
        # log.info("method: %s" % method)
        # log.info("properties: %s" % properties)
        log.info("amqp message from server: %s" % body)

        try:
            message = json.loads(body)
        except ValueError as e:
            log.warn("Received message that is not json")
            return


        if 'stream1' in message:
            self.stream1 = message['stream1']
        if 'stream2' in message:
            self.stream2 = message['stream2']
        if 'stream1quality' in message:
            self.stream1quality = int(message['stream1quality'])
        if 'stream2quality' in message:
            self.stream2quality = int(message['stream2quality'])
        if 'bg_threshold' in message:
            self.bg_threshold = int(message['bg_threshold'])
            self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
        if 'bg_history' in message:
            self.bg_history = int(message['bg_history'])
            self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
        # BUG: Causes full frame to go white
        # if 'bg_detectshadows' in message:
        #     self.bg_detectshadows = bool(message['bg_detectshadows'])
        #     self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
        if 'open_kernel' in message:
            kernel = message['open_kernel'].split(',')
            kernel = (int(kernel[0]), int(kernel[1]))
            self.open_kernel = kernel
        if 'open_iterations' in message:
            self.open_iterations = int(message['open_iterations'])
        if 'erode_kernel' in message:
            kernel = message['erode_kernel'].split(',')
            kernel = (int(kernel[0]), int(kernel[1]))
            self.erode_kernel = kernel
        if 'erode_iterations' in message:
            self.erode_iterations = int(message['erode_iterations'])
        if 'max_size' in message:
            self.max_size = int(message['max_size'])
        if 'min_size' in message:
            self.min_size = int(message['min_size'])
        if 'max_jump_dist' in message:
            self.max_jump_dist = int(message['max_jump_dist'])
            pt.set_tracking_options(max_dist=self.max_jump_dist)
        if 'initial_confidence' in message:
            self.initial_confidence = int(message['initial_confidence'])
            pt.set_tracking_options(initial_confidence=self.initial_confidence)
        if 'confidence_increase' in message:
            self.confidence_increase = int(message['confidence_increase'])
            pt.set_tracking_options(confidence_increase=self.confidence_increase)
        if 'confidence_reduction' in message:
            self.confidence_reduction = int(message['confidence_reduction'])
            pt.set_tracking_options(confidence_reduction=self.confidence_reduction)
        if 'confidence_threshold' in message:
            self.confidence_threshold = int(message['confidence_threshold'])
            pt.set_tracking_options(confidence_threshold=self.confidence_threshold)
        if 'min_confidence' in message:
            self.min_confidence = int(message['min_confidence'])
            pt.set_tracking_options(min_confidence=self.min_confidence)
        if 'max_confidence' in message:
            self.max_confidence = int(message['max_confidence'])
            pt.set_tracking_options(max_confidence=self.max_confidence)


    @gen.coroutine
    def message_handler(self):
        # possible messages from server:
        # - start / stop
        # - player IDs
        # - scene crop dimensions
        # - map image request
        # - tune variable

        while True:
            message = yield self.ws_video.read_message()

            if message is None:
                log.info("Websocket closed")
                self.ptcv.cleanup()
                return

            message = json.loads(message)
            log.info("websocket message from server: %s" % message)

            if 'stream1' in message:
                self.stream1 = message['stream1']
            if 'stream2' in message:
                self.stream2 = message['stream2']
            if 'stream1quality' in message:
                self.stream1quality = int(message['stream1quality'])
            if 'stream2quality' in message:
                self.stream2quality = int(message['stream2quality'])
            if 'bg_threshold' in message:
                self.bg_threshold = int(message['bg_threshold'])
                self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
            if 'bg_history' in message:
                self.bg_history = int(message['bg_history'])
                self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
            if 'bg_detectshadows' in message:
                self.bg_detectshadows = bool(message['bg_detectshadows'])
                self.ptcv.set_background_subtraction(varThreshold=self.bg_threshold, history=self.bg_history, detectShadows=self.bg_detectshadows)
            if 'open_kernel' in message:
                kernel = message['open_kernel'].split(',')
                kernel = (int(kernel[0]), int(kernel[1]))
                self.open_kernel = kernel
            if 'open_iterations' in message:
                self.open_iterations = int(message['open_iterations'])
            if 'erode_kernel' in message:
                kernel = message['erode_kernel'].split(',')
                kernel = (int(kernel[0]), int(kernel[1]))
                self.erode_kernel = kernel
            if 'erode_iterations' in message:
                self.erode_iterations = int(message['erode_iterations'])
            if 'max_size' in message:
                self.max_size = int(message['max_size'])
            if 'min_size' in message:
                self.min_size = int(message['min_size'])
            if 'max_jump_dist' in message:
                self.max_jump_dist = int(message['max_jump_dist'])
                pt.set_tracking_options(max_dist=self.max_jump_dist)
            if 'initial_confidence' in message:
                self.initial_confidence = int(message['initial_confidence'])
                pt.set_tracking_options(initial_confidence=self.initial_confidence)
            if 'confidence_increase' in message:
                self.confidence_increase = int(message['confidence_increase'])
                pt.set_tracking_options(confidence_increase=self.confidence_increase)
            if 'confidence_reduction' in message:
                self.confidence_reduction = int(message['confidence_reduction'])
                pt.set_tracking_options(confidence_reduction=self.confidence_reduction)
            if 'confidence_threshold' in message:
                self.confidence_threshold = int(message['confidence_threshold'])
                pt.set_tracking_options(confidence_threshold=self.confidence_threshold)
            if 'min_confidence' in message:
                self.min_confidence = int(message['min_confidence'])
                pt.set_tracking_options(min_confidence=self.min_confidence)
            if 'max_confidence' in message:
                self.max_confidence = int(message['max_confidence'])
                pt.set_tracking_options(max_confidence=self.max_confidence)

    @gen.coroutine
    def startup(self):
        zone_id = 0
        self.url = "ws://%s:8888/client/0" % pt_server
        self.ws_video = yield websocket_connect(self.url)
        log.info("Connected to pt-server at %s" % self.url)

        if webcam:
            self.ptcv.open_video()
        elif vidfile:
            self.ptcv.open_videofile(vid)

    @gen.coroutine
    def stream_video(self):
        log.info("Starting stream.")

        if not raspberry_pi:
            while True:
                yield self.send_frame()

        # Raspberry pi stills
        # while True:
        #     camera.capture(rawCapture, format="bgr")
        #     frame = rawCapture.array
        #     self.send_frame(frame=frame)
        #     rawCapture.truncate(0)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # import cProfile
            # cProfile.runctx('self.send_frame(frame=frame.array)', globals(), locals())
            self.send_frame(frame=frame.array)
            rawCapture.truncate(0)

    # @gen.coroutine
    # def send_map(self):
    #     # # # Let camera warm up
    #     # for i in range(15):
    #     #     self.ptcv.grab()

    #     img_dict = {
    #         'zone_id': "%s,%s" % (0, 0),
    #         'zone_x': 0,
    #         'zone_y': 0,
    #         'type': 'map'
    #     }
    #     self.ptcv.grab()
    #     img = self.ptcv.retrieve()
    #     img = self.ptcv.cartoonify(img)

    #     frame = self.ptcv.resize(img, (int(res_x/resolution), int(res_y/resolution)))
    #     jpeg_base64 = self.ptcv.np_to_jpeg_base64(frame)
    #     img_dict['frame'] = jpeg_base64
    #     pickled_dict = pickle.dumps(img_dict)

    #     self.ws_video.write_message(pickled_dict)

    @gen.coroutine
    def send_frame(self, frame=None):
        if not send:
            io_loop.call_later(1, self.send_frame)
            return

        img_dict = {
            'zone_id': "%s,%s" % (0, 0),
            'zone_x': 0,
            'zone_y': 0,
        }

        self.count = self.count + 1
        img_dict['frame_id'] = self.count
        img_dict['frame'] = None
        img_dict['time'] = time.time()

        if frame is not None:
            orig_img = frame
        elif webcam:
            self.ptcv.grab()
            grabtime = time.time()
            img_dict['time'] = grabtime
            orig_img = self.ptcv.retrieve()
        elif vidfile:
            orig_img = self.ptcv.read()

        if orig_img is None:
            print "Frame is None"
            return
        sub_bg_img = self.ptcv.backgroundSubtraction(orig_img)
        # noise_reduced_img = self.ptcv.open(sub_bg_img, kernel=self.open_kernel, iterations=self.open_iterations)

        # # Find Players Algorithm
        eroded_img = self.ptcv.erode(sub_bg_img, kernel=self.erode_kernel, iterations=self.erode_iterations)
        all_contours = self.ptcv.find_contours(eroded_img)
        contours = [contour for contour in all_contours if self.ptcv.is_contour_human_sized(contour, max_size=self.max_size, min_size=self.min_size)]
        locs = self.ptcv.trace_multi_moments(contours)
        players = pt.identify_nearest_players(locs)
        img_dict['players'] = players

        eroded_img = self.ptcv.to_color(eroded_img)

        self.ptcv.drawContours(eroded_img, contours)

        # # Add location coords and dot
        i = 1
        for player in players:
            # location listings
            # text_loc = "%s = (%s, %s)" % (i, player['loc'][0], player['loc'][1])
            # text_pos = (0, 30*i)
            # self.ptcv.put_circle(eroded_img, player['loc'], radius=5)
            # self.ptcv.put_text(eroded_img, text_loc, text_pos)
            # player dots
            id_loc = (player['loc'][0] + 20, player['loc'][1] + 10)
            id_text = "%s,%s" % (player['id'][:2], player['confidence'])
            if player['confidence'] >= 10:
                color = (0, 0, 255)
            else:
                color = (0, 255, 255)
            self.ptcv.put_text(eroded_img, id_text, id_loc, color=color)
            i += 1

        # # Put frame count in bottow left corner
        # # count_loc = (5, eroded_img.shape[0] - 11)
        # # self.ptcv.put_text(eroded_img, "%s" % self.count, count_loc)

        streams = {
            'original': orig_img,
            'bg_sub': sub_bg_img,
            'final': eroded_img
        }

        if self.stream1:
            outbound_img = streams[self.stream1]
            jpeg_base64 = self.ptcv.np_to_jpeg_base64(outbound_img, quality=self.stream1quality)
            img_dict['stream1'] = jpeg_base64

        if self.stream2:
            outbound_img = streams[self.stream2]
            jpeg_base64 = self.ptcv.np_to_jpeg_base64(outbound_img, quality=self.stream2quality)
            img_dict['stream2'] = jpeg_base64


        # Grid display
        # for x in range(resolution):
        #     for y in range(resolution):
        #         img_dict['zone_id'] = "%s,%s" % (x, y)
        #         img_dict['zone_x'] = x
        #         img_dict['zone_y'] = y
        #         pickled_dict = pickle.dumps(img_dict)
        #         self.ws_video.write_message(pickled_dict)

        pickled_dict = pickle.dumps(img_dict)
        self.ws_video.write_message(pickled_dict)

        # Send next frame after 1ms delay which gives other tasks a chance to run
        # if not raspberry_pi:
        #     io_loop.call_later(0.1, self.send_frame)

    def cleanup(self):
        if getattr(self, "ws_video", False):
            self.ws_video.close()
        self.connection.close()
        self.ptcv.cleanup()

@gen.coroutine
def main():
    while True:
        log.info("Attempting to connect...")
        try:
            yield zstream.startup()
            # yield zstream.send_map()
            yield zstream.stream_video()
            # yield zstream.message_handler()
        except Exception as e:
            log.info("Got an exception!")
            log.exception(e)
            # Close connection if possible
            if getattr(zstream, "ws_video", False):
                zstream.ws_video.close()
        time.sleep(1)


zstream = ZoneStream()

if __name__ == "__main__":
    try:
        io_loop.run_sync(main)
    except KeyboardInterrupt as e:
        log.info("Shutting down ptclient.")
        io_loop.stop()
        zstream.cleanup()
        io_loop.close()
        sys.exit(0)
        


