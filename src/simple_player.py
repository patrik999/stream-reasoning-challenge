#!/usr/bin/env python

import getopt, sys
import optparse
import time
from abstract_player import AbstractPlayer 

class SimplePlayer(AbstractPlayer):

    rounds = 500

    def init(self, stream_id, template_id):  # __init__
        self.streamID = stream_id
        self.templateID = template_id


    def start(self, freq_in_ms):

        self.frequency = freq_in_ms

        for index in range(self.rounds):
            #print self.constantTexts[index]
            msgText = "Test Msg " + str(index)
            yield msgText
            time.sleep(self.frequency)

    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms

def main(argv):

    player = SimplePlayer("SID", "TID")

    print("Start streaming...")

    for msg in player.start(0): # 0.1
        print(msg)

    print("Stop streaming.")

    player.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
