import subprocess


class TaskRunner():

    '''Base class for wrapping a running task'''

    def __init__(self, task):
        self.execute(task)

    def buildCommand(self, task):
        '''Constructs a command to run from a task'''
        raise NotImplementedError

    def parseProgress(self, line):
        '''Parses the progress of a task from a log line'''
        raise NotImplementedError

    def execute(self, task):
        '''Runs a task'''
        command = self.buildCommand(task)

        # Create a new subprocess for the task.
        # NOTE: Maya is currently outputting on stderr (wat).
        # Need to find a better method of redirecting pipes
        popen = subprocess.Popen(command.split(" "), stderr=subprocess.PIPE)

        # Track the progress of the task through by parsing
        # lines coming from the output pipe
        lines_iterator = iter(popen.stderr.readline, "")
        self.lastProgress = 0
        for line in lines_iterator:
            currentProgress = self.parseProgress(line)
            if currentProgress:
                if currentProgress >= self.lastProgress + 10:
                    print(">>> {0}%".format(currentProgress))
                    self.lastProgress = currentProgress

                    # Update the queue with the task's current progress
                    task.queueTask.progress(currentProgress)

        # Block until the subprocess has finished
        popen.wait()

        # Handle any error codes that arise
        if popen.returncode == 0:
            print("Task complete")
            task.queueTask.complete()
        else:
            task.queueTask.error(popen.returncode)
            print("Task did not complete successfully. Error code:{0}. Command:{1}".format(
                popen.returncode, command))
