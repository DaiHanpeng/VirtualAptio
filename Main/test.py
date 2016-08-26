import sys, os
sys.path.append(os.path.abspath('..'))

from modules.Mqtt.publisher import publisher
from modules.QcRerunInfoParser.QcRerunInfoParser import *

def test():
    parser = QcRerunInfoParser()
    parser.parse()

    print parser

    publisher = QcRerunInfoMqttPublisher()
    publisher.publish(parser.get_rerun_list())

if __name__ == '__main__':
    test()