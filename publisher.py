import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import hashlib, json, time, random, string
from typing import List, Mapping
from copy import deepcopy
from validator import validateDesc, validateId, editTaskValidate
from handler import Handler

"""
    # CO324 LAB6 Pub-Sub With MQTT
    # CHAMITH UKDK  
    # e16057@eng.pdn.ac.lk

    Execution Order
    ----------
    First -> subscriber.py
    Then -> publisher.py

    Note
    ------
    To test the last will and testimony close the 
    terminal of publisher.py (Ctrl+C won't do the job) and 
    observe the output in the subscriber.py terminal. 

    Interrupting the terminal with ctrl+ C will
    prevent executing last will and testimony.
    Ctrl+C interruption will to save the tasks 
    to a .json file

    storing tasks for subscriber -> sub_file.json
    storing tasks for publisher -> pub_file.json

    TOPICS
    -------
    TASK-API/ADD_TASK   
    TASK-API/DEL_TASK
    TASK-API/EDIT_TASK
    TASK-API/PUB_STATUS -> clients subscribed to this topic
        to get the last will and testimony message when
        publisher disconnects

"""


def random_string_generator(str_size):
    return "".join(random.choice(string.ascii_letters) for x in range(str_size))

def test_add(client) -> List[str]:
    """ test for grading add task"""
    ids = []
    for i in range(5):
        description = random_string_generator(20)
        id = hashlib.sha1(description.encode()).hexdigest()
        message = {"id": id, "state": "OPEN", "description": description}

        # validate description of task, return true of valid
        validTask = validateDesc(description)
        if(validTask):
            ids.append(id)
            client.publish("TASK-API/ADD_TASK", json.dumps(message), 1, retain=True)
            time.sleep(1)
    return ids

def test_del(client, ids: List[str], tasks: Mapping[str, Mapping[str, str]]) -> None:
    """ test for grading delete tasks"""
    for id in ids:
        validId = validateId(id, tasks) #  validating the task id
        if validId:
            client.publish("TASK-API/DEL_TASK", id, 1)
    
    # deleting a invalid task id
    validId = validateId("123456789", tasks)
    if validId:
        client.publish("TASK-API/DEL_TASK", id, 1)
        time.sleep(2)

def test_edit(client, ids: List[str], tasks: Mapping[str, Mapping[str, str]]) -> None:
    """ test for grading edit tasks"""
    for i in range(3): # editing first 3 messages
        id = ids[i]
        task = tasks[id]
        task['description'] = "this task was edited "+ str(i)
        validTask = editTaskValidate(task, tasks) # validate the task
        if validTask:
            client.publish("TASK-API/EDIT_TASK", json.dumps(task), 2) # Qos level 2
            time.sleep(2)
    
    # demonstrating state transition
    for i in range(3, 5): # editing last 2 messages
        id = ids[i]
        task = deepcopy(tasks[id]) # getting the deep copy for easy modification

        # OPEN -> ASSIGNED: legal -- OPEN -> PROGRESSING : illegal
        # both transformation demonstrated using a single loop
        task['state'] = "ASSIGNED" if i%2 == 0 else "PROGRESSING"
        validTask = editTaskValidate(task, tasks) # validate the task
        if validTask:
            client.publish("TASK-API/EDIT_TASK", json.dumps(task), 2) # Qos level 2
            time.sleep(2)
    
if __name__ == "__main__":

    # initiating a client
    client1 = mqtt.Client("publisher_1") 

    # initiating handler object to handle callbacks and read, write
    handler = Handler("pub_file.json")

    # assigning callbacks 
    client1.on_message = handler.on_message
    client1.on_connect = handler.on_connect
    client1.on_disconnect = handler.on_disconnect

    # setting last will message upon a unexpected disconnection while publishing
    client1.will_set("TASK-API/PUB_STATUS", "## Publisher went offline", 1, retain=True)

    # connecting to the broker
    try:  # bad ip address or port number will raise an exception
        client1.connect("mqtt.eclipse.org", 1883, 60)
    except:
        print("Connection failed")
        exit(1)

    # subscribe to TASK-API/ADD_TASK  : TASK-API/DEL_TASK : TASK-API/EDIT_TASK : TASK-API/PUB_STATUS
    client1.subscribe("TASK-API/+", 1)


    try:
        client1.loop_start()

        # adding tasks
        id_list = test_add(client1)
        time.sleep(2)

        # editing tasks
        test_edit(client1, id_list, handler.tasks)
        time.sleep(2)

        # deleting tasks
        test_del(client1, id_list, handler.tasks)
        time.sleep(2)

    except: # disconnect upon interruption
        client1.loop_stop()
        client1.disconnect()
    finally: # disconnect after publishing
        client1.loop_stop()
        client1.disconnect()