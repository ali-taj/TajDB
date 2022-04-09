import json
import os
import random
import string
from datetime import datetime

from database import databases_location, CustomersDB


def id_generator(size=18, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def config_data(**kwargs):
    data = {"_id": id_generator(), "_data_storage": kwargs["data_storage"], "_items": kwargs["data"]}
    return data


class Home:

    def search(self, request):
        data_string = request.rfile.read(
            int(request.headers['Content-Length'])) if "Content-Length" in request.headers else ""
        url = request.path

        return {"response": {"url": url, "data": data_string}, "status": 200}


class Customers:

    def get(self, request):
        male_count = 0
        customer_list = CustomersDB.list(CustomersDB)
        for data in customer_list:
            if "gender" in data:
                if data["gender"] == "Male":
                    male_count += 1
        response = {"gender Male Count": male_count, "all_count": len(customer_list)}
        return {"response": response, "status": 200}

    def create(self, request):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            prepared_data_for_save = config_data(data_storage="customers", data=request_data)
            response = CustomersDB.append(CustomersDB, data=prepared_data_for_save)
            return {"response": response, "status": 201}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def list(self, request):
        return {"response": CustomersDB.list(CustomersDB), "status": 200}



class DataBase:
    def size(self, request):
        arr = os.listdir(os.path.dirname(databases_location))
        response = []
        for db in arr:
            json_data = {"database_name": db.replace(".json", "")}

            db_file = open(f'{databases_location}{db}', 'r')
            file_size = os.fstat(db_file.fileno()).st_size
            value_labels = ['bytes', 'Kb', 'Mb', 'Gb', 'Tb']
            value_labels_index = 0
            while file_size > 1024:
                file_size = file_size / 1024
                value_labels_index += 1

            if file_size % (1024 ** value_labels_index) > 0:
                file_size_two_decimal = '{0:.2f}'.format(file_size)
            else:
                file_size_two_decimal = file_size
            json_data["size"] = f"{file_size_two_decimal} {value_labels[value_labels_index]}"

            json_data["create_date"] = datetime.fromtimestamp(
                os.path.getctime(f'{databases_location}{db}')).strftime('%Y-%m-%d %H:%M:%S')
            json_data["last_modify_time"] = datetime.fromtimestamp(
                os.path.getmtime(f'{databases_location}{db}')).strftime('%Y-%m-%d %H:%M:%S')

            response.append(json_data)

        return {"response": response, "status": 200}
