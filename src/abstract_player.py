#!/usr/bin/env python

import getopt, sys
import optparse
import time


# Base class for a reader
class AbstractPlayer:  #__metaclass__ = ABCMeta

    streamID = ""
    templateID = ""
    frequency = 0.1 # Update every 100ms


    def __init__(self, stream_id, template_dictionary):  # template_id
        self.streamID = stream_id
        self.templateID = template_dictionary


    def start(self, freq_in_ms):
        # Here comes the open. This does not need be be overriten
        return

    def stop(self):
        # Here comes the read and yield
        #raise NotImplementedError
        return

    def modify(self, freq_in_ms):
        return
        #def add_noise(self, freq_in_ms):


    def close(self):
        # Here comes the close. This does not need be overriten
        return
