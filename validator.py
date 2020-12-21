from typing import Mapping

#
# Functions for validating id, description and state transition
#

def editTaskValidate(newTask, taskDict) -> bool:
    """ function used to validate a task editing """
    id = newTask['id']
    oldTask = taskDict[id] # get the old task

    validId = validateId(id, taskDict) # valiting id
    validDesc = validateDesc(newTask['description']) # validating description 
    validState = validateState(oldTask['state'], newTask['state']) # validating state transition
    
    # if everything is valid return true, otherwise false
    if validId and validDesc and validState:
        return True
    return False

def validateId(id: str, tasks: Mapping[str, Mapping[str, str]]) -> bool:
    """ function for validating task id """

    if(id in tasks): # id the given id exists return true
        return True
    print(">> Error: Given id does not exist")
    return False

def validateDesc(desc: str) -> bool:
    """ function for validating task description """

    if(len(desc) > 1024):
        print(">> Error: Description must be less than 1024 characters")
        return False
    return True

def validateState(oldState: str, newState: str) -> bool:
    """ Function for validating correct state transition """

    # transition to same state is allowed
    if oldState == newState:
        return True

    # OPEN -> ASSIGNED or OPEN -> CANCELLED
    elif oldState == "OPEN":
        if newState == "ASSIGNED" or newState == "CANCELLED":
            return True                

    # ASSIGNED -> PROGRESSING only
    elif oldState == "ASSIGNED":
        if newState == "PROGRESSING":
            return True

    # PROGRESSING -> DONE or PROGRESSING -> CANCELLED
    elif oldState == "PROGRESSING":
        if newState == "DONE" or newState == "CANCELLED":
            return True

    print(">> Error: Illegal state transition")
    return False
