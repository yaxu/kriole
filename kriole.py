#!/usr/bin/env python

from liblo import *

import sys

import MySQLdb as db

class MyServer(Server):
    def __init__(self):
        Server.__init__(self, 6010)
        self.con = db.connect('localhost', 'kriole', 'kriole', 'kriole')
    
    @make_method('/chunk', 'ififff')
    def chunk_chunk(self, path, args):
        pid, starttime, chunk, v_pitch, v_flux, v_centroid = args
        print "chunk %i = %f, %f, %f" % (chunk, v_pitch, v_flux, v_centroid)

        cur = self.con.cursor()
        cur.execute("insert into chunk (pid, starttime, chunk, v_pitch, v_flux, v_centroid)"
                    + "values (%s, %s, %s, %s, %s, %s)",
                    (pid, starttime, chunk, v_pitch, v_flux, v_centroid)
                    )
        self.con.commit()
        cur.close()
        try:
            target = Address(6040)
            send(target, "/hear",
                 float(v_pitch), 
                 float(v_flux), 
                 float(v_centroid)
                )
        except AddressError, err:
            print str(err)

    @make_method('/play', 'iiiifff')
    def chunk_play(self, path, args):
        pid, sec, usec, lowchunk, v_pitch, v_flux, v_centroid = args
        print "play (%i): %f, %f, %f" % (lowchunk, v_pitch, v_flux, v_centroid)

        cur = self.con.cursor()
#        cur.execute("select v_pitch, v_flux, chunk from chunk "
#                    + "where chunk >= %s and pid = %s "
#                    + "order by abs(v_pitch - %s) limit 1",
#                    (lowchunk, pid, v_pitch)
#                    )
#        cur.execute("select v_pitch, v_flux, chunk from chunk "
#                    + "where chunk >= %s and pid = %s "
#                    + "order by (pow(v_pitch - %s,2)*2) + pow(v_flux - %s,2) limit 1",
#                    (lowchunk, pid, v_pitch, v_flux)
#                    )
        cur.execute("select v_pitch, v_flux, v_centroid, chunk from chunk "
                    + "where chunk >= %s and pid = %s "
                    + "order by (pow(v_centroid - %s,2)*2) + pow(v_pitch - %s,2) limit 1",
                    (lowchunk, pid, v_centroid, v_pitch)
                    )
        (v_pitch, v_flux, v_centroid, chunk) = cur.fetchone()
        print "got values %f, %f, %f at %s" % (v_pitch, v_flux, v_centroid, chunk)

        try:
            target = Address(7771)
            send(target, "/play",
                 sec,
                 usec,
                 "kriole",
                 0.0, # offset
                 0.0, # start
                 1.0, # end
                 1.0, # speed
                 0.5, # pan
                 0.0, # velocity
                 "p",  # vowel
                 0.0, # cutoff
                 0.0, # resonance
                 0.0, # accellerate
                 0.0, # shape
                 int(chunk) # kriole_chunk
                 )

            target = Address(6040)
            send(target, "/say",
                 sec,
                 usec,
                 float(v_pitch), 
                 float(v_flux), 
                 float(v_centroid)
                )

        except AddressError, err:
            print str(err)
            
        cur.close()
        

    @make_method(None, None)
    def fallback(self, path, args):
        print "received unknown message '%s'" % path

    def run(self):
        while True:
            self.recv(100000)

try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.run()

