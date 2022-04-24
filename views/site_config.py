import json
from init.helper import DataBaseCTRL


class Main:
    def __init__(self):
        self.users_db = DataBaseCTRL('site_config')

    def add(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            # slide: list (urls) , about: html, logo: list (urls) , namad: list, banner: url (random select)
            # contact us page text: text, roles: list (text), site_name: text, site_slogan: text
            required_fields = ['name', 'description', 'summary', 'types']
            image_fields = ['image']
            for field in required_fields:
                if field not in request_data:
                    return {"response": {"BAD_REQUEST": f"field {field} does not exist in request data."},
                            "status": 400}

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


class Category:
    def __init__(self):
        self.users_db = DataBaseCTRL('categories')

    def get(self):
        pass