#!/usr/bin/python
import os
import sys
import pika
import time
import json
import pickle
import tornado
import socket
import threading
import netifaces

from tornado import gen
from tornado.websocket import websocket_connect

import vds
import pt
import ptcv
from common import getLogger

# import code
# code.interact(local=locals())

# amqp_host = "192.168.111.154"
# localhost = "127.0.0.1"
# amqp_host = "172.16.6.2"
amqp_host = "ptserver.local"

description = 'collimates video streams and pipes it to a web client'
log = getLogger("pt-server", description, level="info")


def get_link_local_address():
    # Return first link local IP address
    return list(set(
        addr['addr']
        for iface in netifaces.interfaces()
        for addr in netifaces.ifaddresses(iface).get(socket.AF_INET, [])
        if '169.254' in addr.get('addr')
    ))

my_ip = get_link_local_address()
if not my_ip:
    log.critical("No local link address set. You may try the following command:"
                 "\nsudo ifdown eth1:0 && sudo ifup eth1:0")
    sys.exit(1)
my_ip = my_ip[0]

def register_service():
    properties = {
        'ip': my_ip,
        'domain_name': 'ptserver.local.',
        'name': 'Player Tracking Server'
    }
    vds.register_service(properties)

def register_service_in_thread():
    register_service_thread = threading.Thread(target=register_service, args=())
    register_service_thread.daemon = True
    register_service_thread.start()


class ZoneHandler(tornado.websocket.WebSocketHandler):
    connections = set()
    clients = set()
    browsers = set()

    def check_origin(self, origin):
        return True

    def initialize(self, game_map, pt_cv, io_loop, amqp_conn):
        self.amqp_conn = amqp_conn
        self.channel = self.amqp_conn.channel()
        # A fanout exchange broadcasts all the messages to all queues (ie. all clients)
        self.channel.exchange_declare(exchange='clients',
                                      type='fanout')

        self.game_map = game_map
        self.ptcv = pt_cv
        self.io_loop = io_loop

    def open(self, remote_type, remote_id):
        self.remote_type = remote_type
        self.remote_id = remote_id
        self.connections.add(self)
        if remote_type == "client":
            self.clients.add(self)
            message = {
                'new_client': remote_id
            }
            # broadcast client join so that browser can push settings to new client
            # [con.write_message(message) for con in self.connections]
        elif remote_type == "browser":
            self.browsers.add(self)
            message = {
                'settings': load_settings()
            }
            self.write_message(message)
        log.info("Num clients: %s" % len(self.clients))
        log.info("Num browsers: %s" % len(self.browsers))
        log.info("Total connections: %s" % len(self.connections))

    def on_message(self, message):
        if self.remote_type == "client":
            frame_dict = pickle.loads(message)
            ptframe = pt.framedict_to_ptframe(frame_dict)
            [con.write_message(frame_dict) for con in self.browsers]

        elif self.remote_type == "browser":
            message = json.loads(message)
            log.info("websocket message from browser: %s" % message)

            if 'save_settings' in message:
                save_settings(message)
            else:
                # [con.write_message(message) for con in self.clients]
                self.send_amqp(message)

    def on_close(self):
        self.connections.remove(self)
        if self.remote_type == "client":
            self.clients.remove(self)
        elif self.remote_type == "browser":
            self.browsers.remove(self)
        log.info("Connection closed %s. Still %s connection(s)",
                self.request.remote_ip, len(self.connections))
        # log.info("Num clients: %s" % len(self.clients))
        # log.info("Num browsers: %s" % len(self.browsers))
        # log.info("Total connections: %s" % len(self.connections))

    def send_amqp(self, message):
        message = json.dumps(message)
        self.channel.basic_publish(exchange='clients', routing_key='', body=message)

def start_server():
    log.info("Pt-server starting...")

    settings = {
        "autoreload": True
    }

    io_loop = tornado.ioloop.IOLoop.instance()
    pt_cv = ptcv.Ptcv()
    
    credentials = pika.PlainCredentials('guest', 'guest')
    amqp_conn = pika.BlockingConnection(pika.ConnectionParameters(
                host=amqp_host,
                credentials=credentials))


    init_dict = dict(game_map=pt.GameMap(),
                     pt_cv=pt_cv,
                     io_loop=io_loop,
                     amqp_conn=amqp_conn
                     )

    application = tornado.web.Application([
        (r'/(.*)/(.*)', ZoneHandler, init_dict)
            ], **settings)
    port = 8888
    application.listen(port)
    log.info("Pt-server started")
    log.info("Listening on port %s..." % port)
    try:
        io_loop.start()
    except KeyboardInterrupt as e:
        log.info("Shutting down ptserver...")
        io_loop.stop()
        io_loop.close()
        pt_cv.cleanup()
        vds.cleanup()
        log.info("Done.")
        sys.exit(0)

def load_settings():
    settings_dir = 'settings'
    settings = []
    if not os.path.exists(settings_dir):
        return settings

    files = [f for f in os.listdir(settings_dir)]

    for f in files:
        with open(settings_dir + "/" + f) as data_file:
            data = json.load(data_file)
            settings_name = f.split('.')[0]
            data['settings_name'] = settings_name
            settings.append(data)

    return settings

def save_settings(settings):
    settings_dir = 'settings'
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)

    if 'settings_name' in settings:
        settings_name = settings['settings_name']
    else:
        settings_name = "settings"
    settings_filename = "%s/%s.json" % (settings_dir, settings_name)
    with open(settings_filename, 'w') as fp:
        json.dump(settings, fp)

    print "saved settings %s" % settings_filename
    print "saved settings %s" % settings

def main():
    # Register this node's IP address
    register_service_in_thread()

    # Run server
    start_server()

if __name__ == "__main__":
    main()

