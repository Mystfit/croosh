class Task(dict):
    def __init__(self, taskType):
        self.type = taskType
        self.owningJob = None
        self.command = ""

    def toJSON(self):
        '''Converts reference task to JSON format'''
        raise NotImplementedError

    def buildFromQueue(self):
        '''Converts from a queue object to a task'''
        raise NotImplementedError
