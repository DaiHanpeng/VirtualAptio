import paho.mqtt.publish as paho_mqtt_publish


'''
publish.single(topic='',payload='',qos=0,retain=False,hostname='',port=1883,client_id='',keepalive=60,will=None)
'''

class publisher():

    def __init__(self):
        pass

    @staticmethod
    def publish(topic,payload='',hostname='localhost',port=1883):
        paho_mqtt_publish.single(topic=topic,payload=payload,hostname=hostname,port=port)

if __name__ == "__main__":
    publisher.publish('reagent','advia2400_1,Alb,101')
    publisher.publish('reagent','advia2400_1,Alt,102')
    publisher.publish('reagent','advia2400_2,K,600')
    publisher.publish('reagent','advia2400_2,Na,330')

