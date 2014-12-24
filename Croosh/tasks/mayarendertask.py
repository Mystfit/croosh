from Croosh import task, taskrunner, job


class MayaRenderJob(job.Job):

    '''A maya render consists of multiple render tasks for either frames
    or sections of a frame'''

    def __init__(self, name, sceneFile, projectPath, renderPath, frameEnd, frameStart=0, width=None, height=None):
        job.Job.__init__(self, name)
        self.projectPath = projectPath
        self.renderPath = renderPath
        self.createTasks(sceneFile, frameEnd, frameStart, width, height)

    def createTasks(self, scene, frameEnd, frameStart=0, width=None, height=None):
        numFrames = frameEnd - frameStart
        for frame in range(numFrames):
            self.tasks.append(MayaRenderTask(
                jobID=self.jobID,
                width=width,
                height=height,
                frame=frame + frameStart,
                scene=scene,
                projectFolder=self.projectPath,
                renderFolder=self.renderPath
            ))
        print(self.tasks[0].toJSON())


class MayaRenderTaskRunner(taskrunner.TaskRunner):

    def __init__(self, task):
        taskrunner.TaskRunner.__init__(self, task)

    def buildCommand(self, task):
        mayaPath = "/Applications/Autodesk/maya2014/Maya.app/Contents/bin/"
        return "{0}Render {1}".format(mayaPath, task.toCommand())

    def parseProgress(self, line):
        if "%" in line:
            splitLine = line.rstrip().split(" ")
            filtered = [col for col in splitLine if col]
            return round(float(filtered[5][:-1]))
        return None


class MayaRenderTask(task.Task):
    TASK_TYPE = "mayaSingleRender"

    def __init__(self, **kwargs):
        task.Task.__init__(self, MayaRenderTask.TASK_TYPE)
        self.jobID = kwargs["jobID"]
        self.width = kwargs["width"]
        self.height = kwargs["height"]
        self.frame = kwargs["frame"]
        self.scene = kwargs["scene"]
        self.projectFolder = kwargs["projectFolder"]
        self.renderFolder = kwargs["renderFolder"]
        self.queueTask = kwargs["queueTask"] if "queueTask" in kwargs else None

    @staticmethod
    def buildFromQueue(task):
        return MayaRenderTask(
            jobID=task.payload["jobID"],
            width=task.payload["width"],
            height=task.payload["height"],
            frame=task.payload["frame"],
            scene=task.payload["scene"],
            projectFolder=task.payload["projectFolder"],
            renderFolder=task.payload["renderFolder"],
            queueTask=task
        )

    def toJSON(self):
        output = {
            "jobID": self.jobID,
            "scene": self.scene,
            "projectFolder": self.projectFolder,
            "renderFolder": self.renderFolder,
            "frame": self.frame
        }
        output["width"] = self.width
        output["height"] = self.height
        return output

    def toCommand(self):
        optionalCommands = ""

        # Frame width in pixels
        if self.width and self.height:
            optionalCommands += "-x {0} -y {1}".format(self.width, self.height)

        # Build required flags
        command = "-v 5 -r {0} -proj {1} -rd {2} -s {3} -e {4}".format(
            "mr",
            self.projectFolder,
            self.renderFolder,
            self.frame,
            self.frame
        )

        # Add optional flags
        if optionalCommands:
            command += optionalCommands

        # Scene file to render goes at the end
        command += " {0}/scenes/{1}".format(self.projectFolder, self.scene)
        return command
