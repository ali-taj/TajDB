import json
import hashlib

from helper import DataBaseCTRL, config_data


class User:
    def __init__(self):
        self.users_db = DataBaseCTRL('users')

    def signup(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            required_fields = ['user_name', 'password']
            password_fields = ['password']
            unique_fields = ['user_name', 'phone']
            for field in required_fields:
                if field not in request_data:
                    return {"response": {"BAD_REQUEST": f"field {field} does not exist in request data."},
                            "status": 400}

            for field in password_fields:
                if field in request_data:
                    request_data[field] = hashlib.sha256(str(request_data[field]).strip().encode('utf-8')).hexdigest()

            for field in unique_fields:
                if field in request_data:
                    users_list = self.users_db.list()
                    for user in users_list:
                        if field in user:
                            if request_data[field] == user[field]:
                                return {"response": {"BAD_REQUEST": f"field {field} duplicate data found."},
                                        "status": 400}
            # todo send code before sign up
            prepared_data_for_save = config_data(data_storage="users", data=request_data)
            response = self.users_db.append(data=prepared_data_for_save)
            return {"response": response, "status": 201}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def get(self, request, auth):
        male_count = 0
        customer_list = self.users_db.list()
        for data in customer_list:
            if "gender" in data:
                if data["gender"] == "Male":
                    male_count += 1
        response = {"gender Male Count": male_count, "all_count": len(customer_list)}
        return {"response": response, "status": 200}

    def create(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            prepared_data_for_save = config_data(data_storage="customers", data=request_data)
            response = self.users_db.append(data=prepared_data_for_save)
            return {"response": response, "status": 201}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def update(self, request, id, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            response = self.users_db.update(data=request_data, id=id)
            return {"response": response, "status": 201}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def delete(self, request, id, auth):
        response = self.users_db.remove(id)
        return {"response": response, "status": 200}

    def list(self, request, auth):
        return {"response": self.users_db.list(), "status": 200}
