from paho.mqtt.client import Client as PahoMqttClient
from paho.mqtt.client import MQTTv31,MQTTv311
from paho.mqtt.client import MQTTMessage


class MqttClient(PahoMqttClient):

    def __init__(self, client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp"):
        super(MqttClient,self).__init__(client_id, clean_session, userdata, protocol, transport)

        self.on_connect = MqttClient.on_connect_handler
        self.on_disconnect = MqttClient.on_disconnect_handler
        self.on_message = MqttClient.on_message_handler
        self.on_publish = MqttClient.on_publish_handler
        self.on_subscribe = MqttClient.on_subscribe_handler
        self.on_unsubscribe = MqttClient.on_unsubscribe_handdler

    @staticmethod
    def on_connect_handler(client, userdata, flags, rc):
        #print userdata
        print("Connection returned " + str(rc))

    @staticmethod
    def on_disconnect_handler(client, userdata, rc):
        #print userdata
        print("Connection disconnectted returned " + str(rc))

    @staticmethod
    def on_message_handler(client, userdata, message):
        #print userdata
        if isinstance(message,MQTTMessage):
            print 'Message received: \n' + 'topic: ' + message.topic + '\t payload: ' + message.payload

    @staticmethod
    def on_publish_handler(client, userdata, mid):
        #print userdata
        print('message ' + str(mid) + ' published.')

    @staticmethod
    def on_subscribe_handler(client, userdata, mid, granted_qos):
        #print userdata
        print('message ' + str(mid) + ' subscribed.')

    @staticmethod
    def on_unsubscribe_handdler(client, userdata, mid):
        #print userdata
        print('message ' + str(mid) + ' un-subscribed.')

    def start(self):
        self.loop_start()

    def stop(self):
        self.loop_stop()

if __name__ == '__main__':

    #initialization
    client1 = MqttClient()
    client1.connect(host='localhost',port=1883)
    client1.start()

    client2 = MqttClient()
    client2.connect(host='localhost',port=1883)
    client2.start()

    #messages handling
    client1.publish(topic='message1',payload='message1_payload')
    client1.subscribe(topic='message2')

    client2.publish(topic='message2',payload='message2_payload')
    client2.subscribe(topic='message1')

    while True:
        pass