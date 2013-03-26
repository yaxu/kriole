#!/usr/bin/env python

import liblo, sys

# send all messages to port 1234 on the local machine
try:
    target = liblo.Address(6010)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

liblo.send(target, "/play", 
           int(sys.argv[1]), 
           float(sys.argv[2]), 
           float(sys.argv[3]))
