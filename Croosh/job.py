import uuid


class Job():
    '''Class representing one job for processing.
    A job contains multiple tasks.'''

    def __init__(self, name):
        self.name = name
        self.jobID = str(uuid.uuid4())
        self.tasks = []

    def createTasks():
        raise NotImplementedError

    def toJSON(self):
        output = {
            "name": self.name,
            "jobiD": self.jobID,
            "tasks": []
        }
        for task in self.tasks:
            output["tasks"].append(task.toJSON())
        return output
