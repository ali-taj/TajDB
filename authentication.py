import datetime

import jwt
from django.conf import settings

from helper import DataBaseCTRL, string_time_format


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
    try:
        authCode = auth_code.split(" ")[1]
    except:
        authCode = "not defined"

    if authCode == "not defined":
        state_1 = class_name.__class__.__name__ == "User" and class_function == "signup" or class_function == "login" or class_function == "verify"
        state_2 = class_name.__class__.__name__ == "Product" and class_function == "list" or class_function == "get"
        if state_1 or state_2:
            return 200
        else:
            return 403
    else:
        login_database = DataBaseCTRL("login")
        login_list = login_database.list()
        selected_token = ''
        for dictionary in login_list:
            if authCode == dictionary["_items"]["access"]["token"]:
                selected_token = dictionary
        if selected_token != '':

            now_datetime = datetime.datetime.now()
            token_datetime = datetime.datetime.strptime(selected_token["_items"]["access"]["exp"],
                                                        string_time_format)

            if token_datetime < now_datetime:
                return 403
            else:
                user_id = selected_token["_items"]['user_id']
                users_list = DataBaseCTRL("users").list()

                for user in users_list:
                    if user_id == user["_id"]:
                        selected_user = user

                permissions_list = DataBaseCTRL("permissions").list()
                for permission in permissions_list:
                    if selected_user["_items"]["access_level_group"] == permission["name"]:
                        selected_permission = permission
                if selected_permission["name"] == "admin":
                    return 200
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
                        return 403
                    elif auth == 200:
                        return 200
                    else:
                        return auth
        else:
            return 403
