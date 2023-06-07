# import paho.mqtt.publish as publish
 
# MQTT_SERVER = "172.20.10.6"
# MQTT_PATH = "test_channel"
# import time
# while True:
#     directionRobot = input('donnez la direction souhaitez(left,right,forward,backward) : ')
#     publish.single(MQTT_PATH, directionRobot, hostname=MQTT_SERVER) #send data continuously every 3 seconds
#     time.sleep(3)
import paho.mqtt.publish as publish

class publisher():
    def __init__(self):
        self.MQTT_SERVER = "172.20.10.6"
        self.MQTT_PATH = "test_channel"

    def send(self,directionRobot):
        publish.single(self.MQTT_PATH, directionRobot, hostname=self.MQTT_SERVER) #send data 
