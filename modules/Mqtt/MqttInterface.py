
import ConfigParser
import os

from publisher import publisher

class MqttInterface():
    '''
    interface for mqtt.
    '''
    #mqtt parameters.
    PARAMETER_INI_FILE = os.path.abspath('..')+'\\Config'+"\\Parameters.CFG"
    MQTT_SECTION_NAME = r'MQTT'
    MQTT_SERVER = r'Server'
    MQTT_PORT = r'Port'

    mqtt_server = ''
    mqtt_port = ''

    @classmethod
    def publish(cls,topic,payload):
        if not (cls.mqtt_server and cls.mqtt_port):
            cls.build_publisher()

        if cls.mqtt_server and cls.mqtt_port:
            print 'mqtt host: ',cls.mqtt_server, ', mqtt port: ', cls.mqtt_port
            publisher.publish(topic,payload,cls.mqtt_server,cls.mqtt_port)

    @classmethod
    def build_publisher(cls):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(MqttInterface.PARAMETER_INI_FILE)
        if config_parser.has_section(MqttInterface.MQTT_SECTION_NAME):
            cls.mqtt_server = config_parser.get(MqttInterface.MQTT_SECTION_NAME,MqttInterface.MQTT_SERVER)
            cls.mqtt_port = config_parser.get(MqttInterface.MQTT_SECTION_NAME,MqttInterface.MQTT_PORT)


