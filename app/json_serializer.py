import json

__author__ = 'fernando'

class JSONSerializable(object):
    def to_json(self):
        raise NotImplementedError("Implement JSONSerializable.to_json")

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONSerializable):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)
