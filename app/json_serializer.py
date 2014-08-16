import json

__author__ = 'fernando'

class JSONSerializable(object):
    def toJSON(self):
        raise NotImplementedError("Implement JSONSerializable.toJSON")

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONSerializable):
            return obj.toJSON()
        return json.JSONEncoder.default(self, obj)
