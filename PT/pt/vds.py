#!/usr/bin/python
import json
import argparse
import logging
import socket
import sys
import time
import zeroconf

from common import getLogger

#  vds stands for very disco service

# logging.basicConfig(level=logging.DEBUG)
# if len(sys.argv) > 1:
#     assert sys.argv[1:] == ['--debug']
#     logging.getLogger('zeroconf').setLevel(logging.DEBUG)

description = 'Very Disco Service Discover'
log = getLogger("service-discovery", description, level="info")

zc = zeroconf.Zeroconf()
info = None

def cleanup():
    log.info("Deregistering service.")
    zc.unregister_service(info)
    zc.close()

def register_service(properties):
    service_type = properties['type'] if 'type' in properties else "_http._tcp.local."
    short_name = properties['name'] if 'name' in properties else "Default Service Name"
    name = "%s.%s" % (short_name, service_type)
    ip_str = properties['ip'] if 'ip' in properties else "127.0.0.1"
    ip = socket.inet_aton(ip_str)
    port = int(properties['port']) if 'port' in properties else 8888
    weight = int(properties['weight']) if 'weight' in properties else 0
    priority = int(properties['priority']) if 'priority' in properties else 0
    domain_name = properties['domain_name'] if 'domain_name' in properties else "myserv.local." # See http://www.dns-sd.org/ServiceTypes.html

    global info
    info = zeroconf.ServiceInfo(service_type,
                                name,
                                address=ip,
                                port=port,
                                weight=weight,
                                priority=priority,
                                properties=properties,
                                server=domain_name
                                )

    try:
        zc.register_service(info)
    except zeroconf.NonUniqueNameException as e:
        print("Registration of service failed. Name taken")
        sys.exit(1)

    log.info("Registered service: \"%s\" on name \"%s\" at address \"%s\"" %
            (name, domain_name, ip_str))
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "You didn't supply an command. Please see '%s -h' for help." % sys.argv[0]
        sys.exit()

    parser = argparse.ArgumentParser(description='An avahi interface.')
    parser.add_argument('-s', '--set', help='set this node as a zeroconf advertised service given a JSON string')
    parser.add_argument('-g', '--get', help='get all zeroconf nodes', nargs='?')
    args = parser.parse_args()

    if args.set:
        try:
            properties = json.loads(args.set)
        except ValueError as e:
            print "You didn't supply json. Please see '%s -h' for help." % sys.argv[0]
            sys.exit()
        register_service(properties)
    elif args.get:
        pass
        # list_services()
