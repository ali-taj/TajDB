import datetime
import json
import hashlib
import random
import string

from helper import DataBaseCTRL, config_data, send_sms, string_time_format


class Product:
    def __init__(self):
        self.users_db = DataBaseCTRL('products')

    def add(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            return {"response": {"add": request_data}, "status": 200}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def get(self, requesr, id, auth):
        return {"response": {"get": id}, "status": 200}

    def delete(self, request, id, auth):
        response = self.users_db.remove(id)
        return {"response": response, "status": 200}

    def list(self, request, auth):
        if auth != 200:
            query = auth
        return {"response": self.users_db.list()[1], "status": 200}
