import paho.mqtt.client as mqtt
import hashlib
import json
from handler import Handler

"""
    # CO324 LAB6 Pub-Sub With MQTT
    # CHAMITH UKDK
    # e16057@eng.pdn.ac.lk

    How to Run
    ----------
    First -> subscriber.py
    Then -> publisher.py

"""

if __name__ == "__main__":

    # initiating a client
    mqttc = mqtt.Client()

    # creating handler to handle callbacks and read, write
    handler = Handler("sub_file.json")
    
    # assigning callbacks
    mqttc.on_message = handler.on_message
    mqttc.on_connect = handler.on_connect
    mqttc.on_disconnect = handler.on_disconnect

    # connecting to the broker
    try:  # bad ip address or port number will raise an exception
        mqttc.connect("mqtt.eclipse.org", 1883, 60)
    except:
        print("Connection failed")
        exit(1)

    # subscribe to TASK-API/ADD_TASK  : TASK-API/DEL_TASK : TASK-API/EDIT_TASK : TASK-API/PUB_STATUS
    mqttc.subscribe("TASK-API/+", 1)

    try: # stay on loop
        mqttc.loop_forever()
    except: # disconnect upon keyboard interruption
        mqttc.disconnect()