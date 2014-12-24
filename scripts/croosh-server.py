from pymongo import MongoClient
from mongoqueue import MongoQueue


mongo = MongoClient('mongodb://localhost:27017/')
crooshdb = mongo.crooshdb

queue = MongoQueue(
    crooshdb.taskqueue,
    consumer_id="distributor",
    timeout=300,
    max_attempts=3)

for i in range(10):
    queue.put({"module": "maya", "frame": i})


task = queue.next()
task.complete()
print(queue.next())
