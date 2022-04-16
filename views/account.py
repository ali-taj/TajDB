import datetime
import json
import hashlib
import random
import string

from helper import DataBaseCTRL, config_data, send_sms, string_time_format


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
                        if field in user["_items"]:
                            # all user signup status = signup, sms
                            if request_data[field] == user["_items"][field]:
                                if user["_items"]["signup_status"] == "signup":
                                    return {"response": {"BAD_REQUEST": f"field {field} duplicate data found."},
                                            "status": 400}
                                else:
                                    # if sign up status == sms , user must have limit sms count
                                    if user["_items"]["limit_sms_count"] < 5:
                                        code = random.randint(10000, 99999)
                                        user["_items"]["limit_sms_count"] += 1
                                        request_data["code"] = code
                                        request_data["limit_sms_count"] = user["_items"]["limit_sms_count"]
                                        self.users_db.update(data=request_data, id=user["_id"])
                                        message = f'-نام سایت-\nکد اعتبارسنجی ثبت نام: {code}'
                                        send_sms(message, request_data["phone"])
                                        return {"response": {"SUCCESS": "code send successfully."}, "status": 200}
                                    else:
                                        return {"response": {
                                            "NOT_ALLOWED": "you get 5 times code. for more please contact us!"},
                                                "status": 403}

            code = random.randint(10000, 99999)
            request_data["signup_status"] = "sms"
            request_data["code"] = code
            request_data["limit_sms_count"] = 1
            request_data["access_level_group"] = "user"
            prepared_data_for_save = config_data(data_storage="users", data=request_data)
            response = self.users_db.append(data=prepared_data_for_save)
            del response["_items"]["code"]
            del response["_items"]["password"]
            del response["_items"]["limit_sms_count"]
            return {"response": response, "status": 201}
        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def verify(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            required_fields = ['code', 'phone']

            for field in required_fields:
                if field not in request_data:
                    return {"response": {"BAD_REQUEST": f"field {field} does not exist in request data."},
                            "status": 400}

            users_list = self.users_db.list()
            for user in users_list:
                if request_data["phone"] == user["_items"]["phone"]:
                    if user["_items"]["signup_status"] == "signup":
                        return {"response": {"BAD_REQUEST": f"user is now signed up and don't need to verify."},
                                "status": 400}
                    else:
                        if request_data["code"] == user["_items"]["code"]:
                            request_data["signup_status"] = "signup"
                            del request_data["code"]
                            del request_data["phone"]
                            self.users_db.update(data=request_data, id=user["_id"])
                            return {"response": {"SUCCESS": "verify complete."}, "status": 200}
                        else:
                            return {"response": {"NOT_FOUND": "code not found!"}, "status": 404}

        else:
            response = {"error": f"Content-Type {request.headers['Content-Type']} not allowed!"}
            return {"response": response, "status": 400}

    def login(self, request, auth):
        if request.headers['Content-Type'] == "application/json":
            data_string = request.rfile.read(int(request.headers['Content-Length']))
            request_data = json.loads(data_string)
            password_fields = ['password']
            if 'password' not in request_data:
                return {"response": {"BAD_REQUEST": "field password does not exist in request data."},
                        "status": 400}
            if 'user_name' not in request_data and 'phone' not in request_data:
                return {"response": {"BAD_REQUEST": "field user_name/phone does not exist in request data."},
                        "status": 400}
            for field in password_fields:
                if field in request_data:
                    request_data[field] = hashlib.sha256(str(request_data[field]).strip().encode('utf-8')).hexdigest()
            users_list = self.users_db.list()
            for user in users_list:
                if 'user_name' in request_data:
                    user_selector = request_data['user_name'] == user["_items"]["user_name"]
                elif 'phone' in request_data:
                    user_selector = request_data['phone'] == user["_items"]["phone"]
                if user_selector:
                    if user["_items"]["signup_status"] == "signup":
                        if request_data["password"] == user["_items"]["password"]:

                            access_token = {
                                'user_id': user["_id"],
                                'exp': (datetime.datetime.now() + datetime.timedelta(days=0, minutes=15)).strftime(string_time_format),
                                'token': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
                            }
                            refresh_token = {
                                'user_id': user["_id"],
                                'exp': (datetime.datetime.now() + datetime.timedelta(days=30)).strftime(string_time_format),
                                'token': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
                            }
                            login_db = DataBaseCTRL("login")
                            login_data = {"access": access_token, "refresh": refresh_token}
                            prepared_data_for_save = config_data(data_storage="login", data=login_data)
                            login_status = login_db.append(prepared_data_for_save)
                            response_login = {"access": login_status["_items"]["access"]["token"],
                                              "refresh": login_status["_items"]["refresh"]["token"]}
                            return {"response": response_login,
                                    "status": 200}
                        else:
                            return {"response": {"NOT_ALLOWED": "password is incorrect!"},
                                    "status": 403}
                    else:
                        return {"response": {"NOT_ALLOWED": "user is not verified. please verify first!"},
                                "status": 403}
                else:
                    return {"response": {"NOT_ALLOWED": "user not found!"},
                            "status": 403}

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
