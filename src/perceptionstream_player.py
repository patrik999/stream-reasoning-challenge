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

    def __init__(self, stream_id, template_dictionary):
        super().__init__(stream_id, template_dictionary)

        # check format type
        self.format_data = template_dictionary["format"]
        if "context" in template_dictionary:
            self.context = json.load(open(template_dictionary["context"]))

        # read the log file and convert to a list of observations
        od = open(self.streamID + ".json")
        ss = open(self.streamID + ".sensor")
        detections = json.load(od)
        sensors = json.load(ss)

        # print(od)
        # {"image_id": "0000000058", "category_id": 7, "label": "truck","bbox": [175.09146241137856, 182.35644541288679, 48.0617183258659, 26.0792264812871], "score": "28.61"},
        for detection in detections:
            image_id = detection['image_id']
            label = detection['label']
            bbox = detection['bbox']
            score = detection['score']
            result = {'label': label, 'bbox': bbox, 'score': score}

            # observation = self.observations.get(image_id)
            # if observation is None:
            if image_id not in self.observations:
                observation = Observation(image_id)
                observation.add(result)  # adding object detection result

                # {"lat": "49.019702312103", "lon": "8.4435252928258", "alt": "114.12394714355", "roll": "-0.023792", "pitch": "0.012376", "vf": "17.078529727139", "ax": "-0.45926757222713", "ay": "-0.24090805193072"}
                observation.set_sensor(sensors[image_id])  # adding sensor data

                self.observations[image_id] = observation
            else:
                observation.add(result)

        # self.observations = observations

    def start(self, freq_in_ms, replay=False):
        self.frequency = freq_in_ms
        self.stopped = False
        self.replay = replay

        while True:
            for key in sorted(self.observations):
                graph = Graph()
                observation = self.observations[key]
                graph = observation.get_graph(graph, self.streamID)

                # graph.serialize(destination='output.nt', format='n3')
                message = str(graph.serialize(format=self.format_data, context=self.context))
                message = message.replace('\\n', '\n').replace(
                    'b\'', '').replace('\'', '')

                yield message
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

        print("Frequency set to: " + str(freq_in_ms) + " ms")

    def stop(self):

        self.stopped = True
        print("Player is stopped")


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

    def get_graph(self, graph, g_streamId):
        SR_NAMESPACE = 'http://stream-reasoning-challenge.org/'
        VISION_NAMESPACE = 'http://vision.semkg.org/onto/v0.1/'

        second = int(int(self.id) / 10)
        tick = int(self.id) % 10
        timeStamp = Literal('2021-04-10T10:10:' + str(second) + '.' + str(tick))

        streamId = g_streamId.split('/')[-1]

        vehicle_iri = URIRef(SR_NAMESPACE + 'vehicle' + streamId)
        cam_iri = URIRef(SR_NAMESPACE + 'camera' + streamId)
        detector_iri = URIRef(SR_NAMESPACE + 'object_detector')

        class_camera = URIRef(SR_NAMESPACE + 'Camera')
        class_detector = URIRef(SR_NAMESPACE + 'Detector')

        # Camera
        graph.add((vehicle_iri, SOSA.hots, cam_iri))
        graph.add((cam_iri, RDF.type, class_camera))
        graph.add((class_camera, RDFS.subClassOf, SOSA.Sensor))

        # Detector
        graph.add((vehicle_iri, SOSA.hots, detector_iri))
        graph.add((detector_iri, RDF.type, class_detector))
        graph.add((class_detector, RDFS.subClassOf, SOSA.Sampler))

        # location
        lat = self.sensor["lat"]
        lon = self.sensor["lon"]
        individual_location_iri = URIRef(SR_NAMESPACE + 'individual_location_' + self.id)
        individual_location_iri_result = URIRef(individual_location_iri + '_result')
        individual_location_class = URIRef(SR_NAMESPACE + 'IndividualLocation')
        graph.add((individual_location_iri, RDF.type, individual_location_class))
        graph.add((individual_location_class, RDFS.subClassOf, SOSA.Observation))
        graph.add((individual_location_iri, SOSA.resultTime, timeStamp))
        graph.add((individual_location_iri, SOSA.hasResult, individual_location_iri_result))
        graph.add((individual_location_iri_result, RDFS.subClassOf, SOSA.Result))
        graph.add((individual_location_iri_result, URIRef(SR_NAMESPACE + 'lat'), Literal(lat, datatype=XSD.float)))
        graph.add((individual_location_iri_result, URIRef(SR_NAMESPACE + 'long'), Literal(lon, datatype=XSD.float)))

        # Move
        vf = self.sensor["vf"]
        ax = self.sensor["ax"]
        ay = self.sensor["ay"]

        individual_move_iri = URIRef(SR_NAMESPACE + 'individual_move_' + self.id)
        individual_move_iri_result = URIRef(individual_move_iri + '_result')
        individual_move_class = URIRef(SR_NAMESPACE + 'IndividualMove')
        graph.add((individual_move_iri, RDF.type, individual_location_class))
        graph.add((individual_move_class, RDFS.subClassOf, SOSA.Observation))
        graph.add((individual_move_iri, SOSA.hasResult, individual_location_iri_result))
        graph.add((individual_move_iri_result, RDFS.subClassOf, SOSA.Result))
        graph.add((individual_move_iri_result, URIRef(SR_NAMESPACE + 'speed'), Literal(vf, datatype=XSD.float)))
        graph.add((individual_move_iri_result, URIRef(SR_NAMESPACE + 'accelerationX'), Literal(ax, datatype=XSD.float)))
        graph.add((individual_move_iri_result, URIRef(SR_NAMESPACE + 'accelerationY'), Literal(ay, datatype=XSD.float)))
        graph.add((individual_location_iri, SOSA.resultTime, timeStamp))

        # Image
        width_property = URIRef(VISION_NAMESPACE + 'width')
        height_property = URIRef(VISION_NAMESPACE + 'height')
        frame_iri = URIRef(SR_NAMESPACE + 'frame_' + self.id)
        image_iri = URIRef(SR_NAMESPACE + 'image_' + self.id)
        frame_class = URIRef(SR_NAMESPACE + 'Frame')
        graph.add((frame_iri, RDF.type, frame_class))
        graph.add((frame_class, SOSA.subClassOf, SOSA.Observation))
        graph.add((frame_iri, SOSA.hashResult, image_iri))
        graph.add((image_iri, SOSA.subClassOf, SOSA.Result))
        graph.add((image_iri, width_property, Literal('1242', datatype=XSD.Integer)))
        graph.add((image_iri, height_property, Literal('375', datatype=XSD.Integer)))

        # graph.add(frame_iri, SOSA.hasResultTime, , datatype=XSD.dateTime) )
        yolo_iri = URIRef((SR_NAMESPACE + 'cv_algorithm_' + 'YoloV4'))
        graph.add((yolo_iri, RDF.type, SOSA.Procedure))

        detection_class = URIRef(SR_NAMESPACE + 'Detection')
        detection_iri = URIRef(SR_NAMESPACE + 'detection_' + self.id)

        graph.add((detection_iri, SOSA.useProcedure, yolo_iri))
        graph.add((detection_iri, RDF.type, detection_class))
        graph.add((detection_class, RDFS.subClassOf, SOSA.Sampling))
        graph.add((detector_iri, SOSA.madeSampling, detection_iri))

        has_box_property = URIRef(VISION_NAMESPACE + 'hasBox')
        box_x_property = URIRef(VISION_NAMESPACE + 'box_x')
        box_y_property = URIRef(VISION_NAMESPACE + 'box_y')
        is_detection_of_property = URIRef(VISION_NAMESPACE + 'isDetectionOf')
        has_detected_object_property = URIRef(VISION_NAMESPACE + 'hasDetectedObject')
        is_in_property = URIRef(VISION_NAMESPACE + 'isIn');
        labels = {
            "bicycle": "02837983-n",
            "car": "02961779-n",
            "bench": "02832068-n",
            "boat": "02861626-n",
            "toilet": "04453655-n",
            "bear": "02134305-n",
            "train": "04475240-n",
            "person": "00007846-n",
            "umbrella": "04514450-n",
            "knife": "03629343-n",
            "giraffe": "02441664-n",
            "airplane": "02694015-n",
            "parking meter": "03897029-n",
            "sofa": "04263630-n",
            "tennis racket": "04416941-n",
            "backpack": "02772753-n",
            "frank": "07692347-n",
            "banana": "07769568-n",
            "bowl": "02884182-n",
            "skateboard": "04233049-n",
            "bottle": "02879899-n",
            "dog": "02086723-n",
            "frisbee": "03402783-n",
            "doughnut": "07654678-n",
            "bag": "02776843-n",
            "cup": "03152175-n",
            "hand blower": "03488399-n",
            "surfboard": "04370646-n",
            "traffic light": "06887235-n",
            "horse": "03543217-n",
            "motorcycle": "03796045-n",
            "zebra": "02393701-n",
            "teddy": "04406517-n",
            "bus": "02927938-n",
            "chair": "03005231-n",
            "refrigerator": "04077839-n",
            "scissors": "04155119-n",
            "sheep": "02414351-n",
            "pot": "03997420-n",
            "cattle": "02405077-n"
        }

        result_id = 0
        for result in self.results:
            label = labels[result['label'].replace(' ', '')]
            bbox = result['bbox']
            detection_iri_result = URIRef(detection_iri + self.id + '_' + str(result_id))
            box_result_iri = URIRef(detection_iri_result + '_box')
            label_iri = URIRef('http://vision.semkg.org/category/' + label)
            graph.add((detection_iri, SOSA.hasResult, detection_iri_result))
            graph.add((detection_iri_result, has_box_property, box_result_iri))
            graph.add((box_result_iri, box_x_property, Literal(bbox[0], datatype=XSD.float)))
            graph.add((box_result_iri, box_y_property, Literal(bbox[1], datatype=XSD.float)))
            graph.add((box_result_iri, width_property,Literal(bbox[2], datatype=XSD.float)))
            graph.add((box_result_iri, height_property,Literal(bbox[3], datatype=XSD.float)))
            graph.add((box_result_iri, has_detected_object_property, label_iri))

            graph.add((detector_iri, SOSA.madeSampling, detection_iri))
            graph.add((detection_iri, is_detection_of_property, image_iri))
            graph.add((box_result_iri, is_in_property, image_iri))

            result_id += 1
        return graph


def main():
    player = PerceptionStreamPlayer('stream-log-files/perceptionstream/2011_09_26_drive_0015',
                                    {'format': 'json-ld', 'context': 'stream-log-files/perceptionstream/context.json'})
    player.start(1)


if __name__ == '__main__':
    main()
