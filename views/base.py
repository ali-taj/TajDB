import datetime

import jwt
from django.conf import settings

from helper import DataBaseCTRL


def authentication(auth_code, class_name, class_function, data_id):
    # token must have this keys
    # {
    #     "user_id": "aaaaa",
    #     "exp": "date time"
    # }
    # permission map
    # {
    #     "name": "user",
    #     "urls": {
    #         "Customer": {
    #             "get": {
    #                 "create_by": "user id",
    #                 "name": "Qoli"
    #             }
    #         },
    #         "SignUp": {
    #             "get": "all"
    #         }
    #     }
    # }
    authCode = auth_code.split(" ")[1]
    login_list = DataBaseCTRL.list("login")
    for dictionary in login_list:
        if authCode in dictionary.values():
            selected_token = dictionary
    if selected_token:
        try:
            decoded_token = jwt.decode(
                authCode, settings.SECRET_KEY, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return {"response": {"AUTH_FIELD": "authentications field."}, "status": 401}
        except jwt.InvalidTokenError:
            return {"response": {"AUTH_FIELD": "authentications field."}, "status": 401}
        now_datetime = datetime.datetime.now()
        token_datetime = datetime.datetime.utcfromtimestamp(
            decoded_token['exp'])

        if token_datetime < now_datetime:
            return {"response": {"AUTH_FIELD": "authentications field."}, "status": 401}
        else:
            user_id = decoded_token['user_id']
            users_list = DataBaseCTRL("users")
            for user in users_list:
                if user_id == user["_id"]:
                    selected_user = user
            permissions_list = DataBaseCTRL("permissions")
            for permission in permissions_list:
                if selected_user["access_level_group"] == permission["name"]:
                    selected_permission = permission

            if selected_permission["name"] == "admin":
                return "True"
            else:
                auth_403 = 0
                auth = 403

                for permission_url in selected_permission['urls']:
                    if class_name == permission_url:
                        for permission_function in selected_permission['urls'][permission_url]:
                            if class_function == permission_function:
                                if selected_permission['urls'][permission_url][permission_function] == "all":
                                    auth = 200
                                else:
                                    for json_query in selected_permission['urls'][permission_url][permission_function]:
                                        auth = json_query
                                pass
                            else:
                                auth_403 += 1

                    else:
                        auth_403 += 1
                if auth_403 > 0:
                    auth = 403 if auth_403 == len(selected_permission['urls']) else 200
                if auth == 403:
                    return {"error": "you don't have permissions for this request!"}
                elif auth == 200:
                    return "True"
                else:
                    return auth
    else:
        return {"error": "auth failed"}