from pymongo import MongoClient
from mongoqueue import MongoQueue
import threading
import time
from Croosh.tasks.mayarendertask import MayaRenderTask, MayaRenderTaskRunner


class Machine(threading.Thread):
    '''A machine represents one worker on the network.
    Depending on the incoming task, will spawn an appropriate task processor.
    It WILL NOT add tasks to the queue.'''

    def __init__(self, name):
        threading.Thread.__init__(self, name=name)
        self.exitFlag = 0
        self.setDaemon(True)

        #  Mongo connection
        mongo = MongoClient('mongodb://localhost:27017/')
        self.db = mongo.crooshdb
        self.taskqueue = MongoQueue(
            self.db.taskqueue,
            consumer_id=name,
            timeout=300,
            max_attempts=3)

        # Active tasks
        self.activeTask = None
        self.taskRunner = None
        self.acceptsTasks = True
        self.register()

    def register(self):
        '''Adds machine to list of active machines on DB'''
        self.db.machines.find_and_modify(
            query={"_id": self.name},
            update={"$setOnInsert": {
                "_id": self.name,
                "activeTask": None,
                "acceptsTasks": True
            }},
            upsert=True,
            new=True
        )

    def run(self):
        self.listen()

    def close(self):
        self.exitFlag = 1
        print("Cleanup complete")

    def listen(self):
        print("Machine listening for tasks...")
        while not self.exitFlag:
            self.pollTasks()
            time.sleep(2)
        self.join()

    def pollTasks(self):
        if not self.taskRunner:
            task = self.taskqueue.next()
            if task:
                # Set active task for machine
                taskWrapper = MayaRenderTask.buildFromQueue(task)
                print("Running task {0}".format(taskWrapper.jobID))

                self.updateMachineStatus(task)
                self.taskRunner = MayaRenderTaskRunner(taskWrapper)

                # Clear task for machine on completion and reregister to queue
                self.updateMachineStatus(None)
                self.taskRunner = None

    def updateMachineStatus(self, task=None):
        self.acceptsTasks = False if task else True
        self.db.machines.find_and_modify(
            query={"_id": self.name},
            update={
                "activeTask": task.job_id if task else None,
                "acceptsTasks": self.acceptsTasks
            }
        )


if __name__ == "__main__":
    machine = Machine("test_machine")
    try:
        machine.listen()
    except KeyboardInterrupt:
        machine.close()
