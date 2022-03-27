import getopt, sys, os
import optparse
import time
from abstract_player import AbstractPlayer
import json
ROOT_PATH = os.path.abspath(os.curdir) + "/"

class Comma2k19Player(AbstractPlayer):
    format_data = "ttl"

    def init(self, stream_id, template_id):  # __init__
        super().__init__(stream_id, template_dictionary)
        self.format_data = template_dictionary["format"]

    def start(self, freq_in_ms, replay=False):
        '''Modify this function according to your needs.'''
        self.frequency = freq_in_ms
        self.stopped = False
        self.replay = replay

        # Load the dataset
        # dataset = load_the_dataset()  # TODO use your own function/code

        # Prepare the dataset (as explained in this notebook)
        # df = prepare_dataset(dataset)  # TODO use your own function/code

        # Open one by one the ttl files

        #rdf_files = sorted([int(d.name) for d in os.scandir(ROOT_PATH+self.streamID) if d.is_dir()])  # get all the available segment numbers
        rdf_files = os.listdir(ROOT_PATH+self.streamID)

        while True:
            for file_name in rdf_files:
                if file_name == "kb.ttl":
                    continue
                with open(self.streamID + '/' + file_name) as f:
                    data = f.read()
                    

                message=""
                if self.format_data=="ttl":
                    message = data
                else:
                    print('Format is not supported!')

                yield message
                print(message)
                time.sleep(self.frequency / 1000.0)

                # Check if stopped
                if (self.stopped):
                    break

            if (not self.replay or self.stopped):
                break
            else:
                print("Simulation restart.")
                time.sleep(1)

    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms
