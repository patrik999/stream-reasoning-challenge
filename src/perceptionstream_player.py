from abstract_player import AbstractPlayer
from rdflib import Graph, URIRef, Literal, plugin
from rdflib.serializer import Serializer
from rdflib.namespace import SSN, SOSA, RDF, RDFS, XSD
import json
import time


class PerceptionStreamPlayer(AbstractPlayer):
    observations = {}
    format_data = "n3"
    context = None
    templates = {}

    def __init__(self, stream_id, template_dictionary):
        super().__init__(stream_id, template_dictionary)
        self.templates = template_dictionary
        # check format type
        self.format_data = template_dictionary["format"]
        if "context" in template_dictionary:
            self.context = json.load(open(template_dictionary["context"]))

        # read the log file and convert to a list of observations
        od = open(self.streamID+".json")
        ss = open(self.streamID+".sensor")
        detections = json.load(od)
        sensors = json.load(ss)
        #self.observations = {}

        # {"image_id": "0000000058", "category_id": 7, "label": "truck","bbox": [175.09146241137856, 182.35644541288679, 48.0617183258659, 26.0792264812871], "score": "28.61"},
        for detection in detections:
            image_id = detection['image_id']
            label = detection['label']
            bbox = detection['bbox']
            score = detection['score']
            result = {'label': label, 'bbox': bbox, 'score': score}

            #observation = self.observations.get(image_id)
            # if observation is None:
            if image_id not in self.observations:
                observation = Observation(image_id)
                observation.add(result)  # adding object detection result

                #{"lat": "49.019702312103", "lon": "8.4435252928258", "alt": "114.12394714355", "roll": "-0.023792", "pitch": "0.012376", "vf": "17.078529727139", "ax": "-0.45926757222713", "ay": "-0.24090805193072"}
                observation.set_sensor(sensors[image_id])  # adding sensor data

                self.observations[image_id] = observation
            else:
                observation.add(result)

        #self.observations = observations

    def start(self, freq_in_ms, replay=False):
        self.frequency = freq_in_ms
        self.stopped = False
        self.replay = replay

        while True:
            for key in sorted(self.observations):
                graph = Graph()
                observation = self.observations[key]
                graph = observation.get_graph(graph)
                #graph.serialize(destination='output.nt', format='n3')
                message = str(graph.serialize(
                    format=self.format_data, context=self.context))
                message = message.replace('\\n', '\n').replace(
                    'b\'', '').replace('\'', '')
                # print(message)

                yield message
                time.sleep(self.frequency / 1000.0)
                # Check if stopped
                if(self.stopped):
                    break

            if(not self.replay or self.stopped):
                break
            else:
                print("Simulation restart.")
                time.sleep(1)

    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms

        print("Frequency set to: " + str(freq_in_ms) + " ms")

    def stop(self):

        self.stopped = True
        print("Player is stopped")

    def getkb(self):
        if "backgroundKB" in self.templates:
            kbName = self.templates["backgroundKB"]
            kbText = open(kbName).read()
            return kbText
        else:
            return ""


class Observation():
    id = ''
    results = []

    def __init__(self, id):
        self.id = id
        self.results = []
        self.sensor = {}

    def add(self, result):
        self.results.append(result)

    def set_sensor(self, sensor):
        self.sensor = sensor

    def length(self):
        return self.results.length

    def get_graph(self, graph):
        SR_NAMESPACE = 'http://stream-reasoning-challenge.org'
        VISION_NAMESPACE = 'http://vision.semkg.org'

        observation_iri = URIRef(SR_NAMESPACE + '/observation/' + self.id + '')
        frame_iri = URIRef(SR_NAMESPACE + '/frame/' + self.id + '')
        yolo_v4_iri = URIRef(SR_NAMESPACE + '/detector/' + 'YoloV4')

        detection_class_iri = URIRef(VISION_NAMESPACE + '/Detection')
        is_detection_of = URIRef(VISION_NAMESPACE + '/isDetectionOf')
        has_detected_object = URIRef(VISION_NAMESPACE + '/hasDetectedObject')
        has_box = URIRef(VISION_NAMESPACE + '/hasBox')
        image2d_iri = URIRef(VISION_NAMESPACE + '/Image2D')
        is_in = URIRef(VISION_NAMESPACE + '/isIn')
        box_x = URIRef(VISION_NAMESPACE + '/box/x')
        box_y = URIRef(VISION_NAMESPACE + '/box/y')
        box_width = URIRef(VISION_NAMESPACE + '/box/width')
        box_height = URIRef(VISION_NAMESPACE + '/box/height')

        graph.add((observation_iri, RDF.type, SOSA.Observation))
        graph.add((observation_iri, SOSA.usedProcedure, yolo_v4_iri))
        graph.add((yolo_v4_iri, RDF.type, SOSA.Procedure))
        graph.add((yolo_v4_iri, RDFS.label, Literal('YoloV4')))
        graph.add((frame_iri, RDF.type, image2d_iri))
        graph.add((detection_class_iri, RDFS.subClassOf, SOSA.Result))

        lat = self.sensor["lat"]
        lon = self.sensor["lon"]
        alt = self.sensor["alt"]
        roll = self.sensor["roll"]
        pitch = self.sensor["pitch"]
        vf = self.sensor["vf"]
        ax = self.sensor["ax"]
        ay = self.sensor["ay"]

        result_id = 0
        for result in self.results:
            # print(result)
            label = result['label'].replace(' ', '')
            bbox = result['bbox']

            detection_result_iri = URIRef(
                SR_NAMESPACE + '/detection/' + self.id + '/' + str(result_id))
            box_result_iri = URIRef(
                SR_NAMESPACE + '/box/' + self.id + '/' + str(result_id))
            detected_object = URIRef(
                SR_NAMESPACE + '/detectedObject/' + label + '/')

            graph.add((observation_iri, SOSA.hasResult, detection_result_iri))
            graph.add((detection_result_iri, RDF.type, detection_class_iri))
            graph.add(
                (detection_result_iri, has_detected_object, detected_object))
            graph.add((detection_result_iri, has_box, box_result_iri))
            graph.add((detected_object, RDFS.label, Literal(label)))

            graph.add((box_result_iri, box_x, Literal(
                bbox[0], datatype=XSD.float)))
            graph.add((box_result_iri, box_y, Literal(
                bbox[1], datatype=XSD.float)))
            graph.add((box_result_iri, box_width,
                      Literal(bbox[2], datatype=XSD.float)))
            graph.add((box_result_iri, box_height,
                      Literal(bbox[3], datatype=XSD.float)))

            graph.add((detection_result_iri, is_detection_of, frame_iri))
            graph.add((box_result_iri, is_in, frame_iri))

            result_id += 1
        return graph


def main():
    player = ObjectDetection(
        'stream-log-files/perceptionstream/2011_09_26_drive_0015', 'n3')
    player.start(1)


if __name__ == '__main__':
    main()
