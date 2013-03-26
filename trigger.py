#!/usr/bin/env python

import liblo, sys, time

# send all messages to port 1234 on the local machine
try:
    target = liblo.Address(7771)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

now = time.time()
now_sec = int(now)
now_usec = int((now - now_sec) * 1000000.0)

liblo.send(target, "/kriole",
           now_sec,
           now_usec,
           float(sys.argv[1]), 
           float(sys.argv[2]), 
           float(sys.argv[3])
           )
#lo_server_thread_add_method(st, "/kriole", "iifff",
