import json

databases_location = 'databases/'


class CustomersDB:
    def __init__(self):
        self.name = customers
        self.location = databases_location + self.name + ".json"

    def list(self):
        file = open(self.location, 'r')
        response_file = json.loads(file.read())
        file.close()
        return response_file

    def update(self):
        pass

    def remove(self):
        pass

    def append(self, data):
        DB_data = json.loads(open(f"{databases_location}customers.json", 'r').read())
        DB_data.append(data)
        DB_data.close()
        DB_file = open(self.location, 'w')
        DB_file.write(json.dumps(DB_data))
        DB_file.close()
        return data
