import json
import os
from datetime import datetime


class JsonCustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JsonDeserializer:
    @staticmethod
    def datetime_parser(dct):
        for key, value in dct.items():
            if isinstance(value, list) and len(value) == 2:
                try:
                    value[1] = datetime.fromisoformat(value[1])
                except (ValueError, TypeError):
                    pass
        return dct

    @classmethod
    def loads(cls, json_file):
        return json.load(json_file, object_hook=cls.datetime_parser)


def save_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, cls=JsonCustomEncoder)


def load_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return JsonDeserializer.loads(file)
    return {}
