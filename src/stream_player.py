#!/usr/bin/env python

import getopt, sys
import optparse
import time


# Base class for a reader
class AbstractPlayer:  #__metaclass__ = ABCMeta

    streamID = ""
    templateID = ""
    frequency = 0.1 # Update every 100ms


    def __init__(self, stream_id, template_id):  #
        self.streamID = stream_id
        self.templateID = template_id


    def start(self, freq_in_ms):
        # Here comes the open. This does not need be be overriten
        a = ""

    def stop(self):
        # Here comes the read and yield
        #raise NotImplementedError
        a = ""

    def close(self):
        # Here comes the close. This does not need be overriten
        a = ""



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
