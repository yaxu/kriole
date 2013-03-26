#!/usr/bin/env python

from liblo import *

import sys

import MySQLdb as db

class MyServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 6010)
        self.con = db.connect('localhost', 'kriole', 'flaphead', 'kriole')
    
    @make_method('/chunk', 'ififf')
    def chunk_chunk(self, path, args):
        pid, starttime, chunk, v_pitch, v_flux = args
        print "chunk %i = %f, %f" % (chunk, v_pitch, v_flux)

        cur = self.con.cursor()
        cur.execute("insert into chunk (pid, starttime, chunk, v_pitch, v_flux)"
                    + "values (%s, %s, %s, %s, %s)",
                    (pid, starttime, chunk, v_pitch, v_flux)
                    )
        self.con.commit()
        cur.close()

    @make_method('/play', 'iiiiff')
    def chunk_play(self, path, args):
        pid, sec, usec, lowchunk, v_pitch, v_flux = args
        print "play (%i): %f, %f" % (lowchunk, v_pitch, v_flux)

        cur = self.con.cursor()
        cur.execute("select v_pitch, v_flux, chunk from chunk "
                    + "where chunk >= %s and pid = %s "
                    + "order by abs(v_pitch - %s) + abs(v_flux - %s) limit 1",
                    (lowchunk, pid, v_pitch, v_flux)
                    )
        (v_pitch, v_flux, chunk) = cur.fetchone()
        print "got values %f, %f at %s" % (v_pitch, v_flux, chunk)

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
                 "",  # vowel
                 0.0, # cutoff
                 0.0, # resonance
                 0.0, # accellerate
                 0.0, # shape
                 int(chunk) # kriole_chunk
                 )
        except AddressError, err:
            print str(err)
            
        cur.close()
        

    @make_method(None, None)
    def fallback(self, path, args):
        print "received unknown message '%s'" % path

try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()
raw_input("press enter to quit...\n")
