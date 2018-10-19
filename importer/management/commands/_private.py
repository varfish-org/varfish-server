import json


class TsvReader:
    def __init__(self, file, json_fields=[]):
        self.fh = open(file, "r")
        self.header = []
        self.json_fields = json_fields
        next(self)

    def __enter__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        fields = next(self.fh).rstrip().split()

        if not self.header:
            self.header = fields
            return

        ret = dict(zip(self.header, fields))

        for json_field in self.json_fields:
            ret[json_field] = json.loads(ret[json_field])

        return ret

    def __exit__(self, exc_type, exc_value, traceback):
        self.fh.close()
