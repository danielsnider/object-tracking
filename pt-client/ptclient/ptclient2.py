#!/usr/bin/python
import sys
import time
import tornado.websocket
import pickle
import time

from tornado import gen
from tornado.websocket import websocket_connect

from ptcv import ptcv
from pt.common import getLogger

description = 'pt-client sends camera frames the central pt server'
log = getLogger("pt-client", description, level="debug")


class ZoneStream(object):
    def __init__(self):
        self.ptcv = ptcv.Ptcv()
    
    @gen.coroutine
    def initialize_connections(self):
        zone_id = 1
        url = "ws://localhost:8888/zone/video/%s" % zone_id
        self.ws_video = yield websocket_connect(url)
        log.info("Connected to pt-server at %s" % url)
        self.ptcv.open_video2()

    @gen.coroutine
    def stream_video(self):
        log.info("Streaming video...")
        count = 0
        while(1):
            count = count + 1
            self.ptcv.grab2()
            grabtime = time.time()
            img = self.ptcv.retrieve2()
            p1loc = self.ptcv.get_p1loc(img)
            p2loc = self.ptcv.get_p2loc(img)
            p3loc = self.ptcv.get_p3loc(img)
            p4loc = self.ptcv.get_p4loc(img)
            players = []
            # green
            if p1loc:
                p1 = {
                    'name':'Green',
                    'x': p1loc[0],
                    'y': p1loc[1]
                }
                players.append(p1)
            # orange
            if p2loc:
                p2 = {
                    'name':'Orange',
                    'x': p2loc[0],
                    'y': p2loc[1]
                }
                players.append(p2)
            # blue
            if p3loc:
                p3 = {
                    'name':'Blue',
                    'x': p3loc[0],
                    'y': p3loc[1]
                }
                players.append(p3)
            # red
            if p4loc:
                p4 = {
                    'name':'Red',
                    'x': p4loc[0],
                    'y': p4loc[1]
                }
                players.append(p4)
            img_dict = {
                'time': grabtime,
                'frame': img.tostring(),
                'frame_id': count,
                'zone_id': 1,
                'zone_x': 1,
                'zone_y': 0,
                'players': players
            }
            pickled_dict = pickle.dumps(img_dict)
            self.ws_video.write_message(pickled_dict)


@gen.coroutine
def main():
    zstream = ZoneStream()
    yield zstream.initialize_connections()
    yield zstream.stream_video()

if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.run_sync(main)