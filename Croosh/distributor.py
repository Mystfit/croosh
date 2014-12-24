from pymongo import MongoClient
from mongoqueue import MongoQueue
from Croosh.tasks.mayarendertask import MayaRenderJob


class Distributor():
    def __init__(self):
        self.mongo = MongoClient('mongodb://localhost:27017/')
        crooshdb = self.mongo.crooshdb
        self.taskqueue = MongoQueue(
            crooshdb.taskqueue,
            consumer_id="distributor",
            timeout=300,
            max_attempts=3)

    def addJob(self, job):
        for task in job.tasks:
            self.taskqueue.put(task.toJSON())

if __name__ == "__main__":
    testDistributor = Distributor()
    testJob = MayaRenderJob(
        "testRender",
        "testScene.ma",
        "/Users/mystfit/Desktop/testRenders",
        "/Users/mystfit/Desktop/renders",
        24)
    testDistributor.addJob(testJob)
