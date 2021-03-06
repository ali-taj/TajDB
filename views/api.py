import base64
import os
from datetime import datetime

import requests

from init.helper import DataBaseCTRL, databases_location, config_data


class DataBase:
    def size(self, request, auth):
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


class DKProducts:

    def __init__(self):
        self.products_db = DataBaseCTRL('products')
        self.dk_products_db = DataBaseCTRL('dk_products')

    def get(self, request, auth):

        active_count = 0
        product_list = self.products_db.list()
        for data in product_list:
            if "status" in data:
                if data["status"] == "marketable":
                    active_count += 1
        response = {"gender Male Count": active_count, "all_count": len(product_list )}
        return {"response": response, "status": 200}

    def get_dg_product(self, request, auth):
        for i in range(109204, 9000000):
            print(i)
            url = f"https://api.digikala.com/v1/product/{i}/"
            url_request = requests.get(url).json()
            if "data" in url_request:
                product_data = url_request["data"]["product"]
                if "is_inactive" not in product_data and product_data["status"] == "marketable":
                    dk_base64_url = base64.b64encode(bytes(f'https://www.digikala.com/product/dkp-{i}', 'utf-8'))
                    main_affiliate_url = "https://affstat.adro.co/click/1eea7fa4-ee12-435b-958c-e4727a721a7e/"
                    data_for_save = {"id": product_data["id"],
                                     "dk_url": "https://www.digikala.com{}".format(product_data["url"]["uri"]),
                                     "affilator_url": f"{main_affiliate_url}{dk_base64_url}"}
                    prepared_data_for_save = config_data(data_storage="dk_products", data=data_for_save)
                    self.dk_products_db.append(data=prepared_data_for_save)
        return {"response": f"{i} products created!", "status": 201}
