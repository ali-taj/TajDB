import json
import random
import string
import requests

databases_location = 'databases/'
string_time_format = "%Y/%m/%d-%H:%M:%S"

def id_generator(size=18, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def config_data(**kwargs):
    data = {"_id": id_generator(), "_data_storage": kwargs["data_storage"], "_items": kwargs["data"]}
    return data


class DataBaseCTRL:
    def __init__(self, db_name):
        self.name = db_name
        self.location = databases_location + self.name + ".json"

    def list(self):
        file = open(self.location, 'r')
        response_file = json.loads(file.read())
        file.close()
        return response_file

    def update(self, data, id):
        DB_data_file = open(f"{databases_location}{self.name}.json", 'r')
        DB_data = json.loads(DB_data_file.read())
        response_data = {"NOT_FOUNT": f"{self.name} with id {id} not found!"}
        for i in range(len(DB_data)):
            if id == DB_data[i]["_id"]:
                for key in data:
                    DB_data[i]["_items"][key] = data[key]
                response_data = DB_data[i]
        DB_file = open(self.location, 'w')
        DB_file.write(json.dumps(DB_data))
        DB_file.close()
        return response_data

    def remove(self, id):
        DB_data_file = open(f"{databases_location}{self.name}.json", 'r')
        DB_data = json.loads(DB_data_file.read())
        for i in range(len(DB_data)):
            if id == DB_data[i]["_id"]:
                DB_data.pop(i)
        DB_data_file.close()
        DB_file = open(self.location, 'w')
        DB_file.write(json.dumps(DB_data))
        DB_file.close()
        return {"deleted": 1, "id": id}

    def append(self, data):
        DB_data = json.loads(open(f"{databases_location}{self.name}.json", 'r').read())
        DB_data.append(data)
        DB_file = open(self.location, 'w')
        DB_file.write(json.dumps(DB_data))
        DB_file.close()
        return data


smsPanelUrl = 'http://smspanel.Trez.ir/SendMessageWithUrl.ashx'
smsPanelUserName = 'Nowian'
smsPanelPassword = 'A2980580457@'
smsPanelPhoneNumber = "50002210003000"

adminPhone = '09375908653'


def send_sms(message, phone):
    requests.get('{}?Username={}&Password={}&PhoneNumber={}&MessageBody={}&RecNumber={}&Smsclass=1'
    .format(smsPanelUrl, smsPanelUserName, smsPanelPassword, smsPanelPhoneNumber,message, phone))
