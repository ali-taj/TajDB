import json

databases_location = 'databases/'


class Selector:
    def _json(self, name):
        file = open(f"{databases_location}{name}.json", 'r')
        response_file = json.loads(file.read())
        file.close()
        return response_file


