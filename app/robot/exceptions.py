__author__ = 'fernando'

class UFSCBlockException(Exception):
    def __init__(self):
        super(UFSCBlockException, self).__init__("UFSC is blocking the request")