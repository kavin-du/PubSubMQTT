import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import hashlib, json, time, random, string
from validator import validateDesc, validateId
from typing import List

class Handler:
    """ Handler class to handler all the callbacks and file read, write """
    
    def __init__(self, taskFile: str):
        self.taskFile = taskFile #  file name to save tasks
        self.tasks = {}

    # The callback when the client reveives a CONNACK response from the server
    def on_connect(self, mqttc, obj, flags, rc):
        if(rc == 0):
            print("connected ok")
            #loading tasks from file when client connect to the broker
            with open(self.taskFile, "r") as f:
                data = f.read()
                if data:
                    self.tasks = json.loads(data)
                    print("Tasks loaded from file "+self.taskFile)
                else: 
                    print("Initial file is empty")
        else:
            print("bad connection")

    # the callback when the PUBLISH message is received from the server
    def on_message(self, mqttc, obj, msg):
        if (msg.topic == "TASK-API/ADD_TASK"):
            print("[+] Adding a Task....")
            task = json.loads(msg.payload.decode("utf-8")) # getting the task
            self.tasks[task['id']] = task  # updating the task dict
        elif (msg.topic == "TASK-API/EDIT_TASK"):
            print("[*] Editing a Task....")
            task = json.loads(msg.payload.decode("utf-8")) # getting the task
            self.tasks[task['id']] = task # updating the task dict
        elif (msg.topic == "TASK-API/DEL_TASK"):
            print("[-] Deleting a Task....")
            id = msg.payload.decode("utf-8") # get the id
            if id in self.tasks:
                self.tasks.pop(id) # delete task from the task dict
        else: # printing the last will message
            print(msg.payload.decode("utf-8"))

    # callback executed after message publication
    def on_publish(self, client, userdata, mid):
        print("data published")

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " qos:" + str(granted_qos))

    # callback when client disconnect from broker
    def on_disconnect(self, client, userdata, rc):
        print("disconnected. code: "+str(rc))

        # when a client disconnects, save everything to a json file
        with open(self.taskFile, "w") as f:
            json.dump(self.tasks, f, indent=4)
            print("Tasks saved to file: "+self.taskFile)
        client.loop_stop() # stopping the loop 
        # print(self.tasks.values()) # printing all the tasks
