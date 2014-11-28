import json

__author__ = 'fernando'

class JSONSerializable(object):
    def to_json(self):
        raise NotImplementedError("Implement JSONSerializable.to_json")


class JSONEncoder(json.JSONEncoder):

    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='utf-8', default=None):
        super(JSONEncoder, self).__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent,
                                          separators, encoding, self.default_encoder)

    def default_encoder(self, obj):
        if isinstance(obj, JSONSerializable):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)
