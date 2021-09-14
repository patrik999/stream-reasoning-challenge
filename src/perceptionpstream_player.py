#!/usr/bin/env python

from abstract_player import AbstractPlayer
import getopt
import sys
import optparse
import time
import json
import os
ROOT_DIR = os.path.abspath(os.curdir)


class PerceptionStreamPlayer(AbstractPlayer):

    def init(self, stream_id, template_id):  # __init__
        self.streamID = stream_id
        self.templateID = template_id

    def start(self, freq_in_ms):

        self.frequency = freq_in_ms
        for log in os.listdir(ROOT_DIR+"/"+self.streamID):
            with open(ROOT_DIR+"/"+self.streamID+"/"+log) as f:
                data = f.read().split("\n")
                data.pop()
            for line in data:
                msgText = line
                yield msgText
                time.sleep(self.frequency/1000.0)

    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms
