from planner import models

class PlannerService(object):
    def __init__(self, user):
        self.user = user

    def run(self):
        # check for all incomplete events that have need a reminder or have passed
        # those that need a reminder create a notification
        # those that have passed a different notification
        pass