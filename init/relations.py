from helper import DataBaseCTRL


def relation_controller(**kwargs):
    # relation_document = {
    #     "target_database": ,
    #     "target_field": ,  # "field1.object.object"
    #     "target_id": ,
    #     "base_database": ,
    #     "base_id":  # ["field1", "field2.object"]
    # }

    selected_document = DataBaseCTRL(kwargs["target_database"]).get_by_id(kwargs["target_id"])

    target_field_list = kwargs['target_field'].split(".")
    field_object_index = 0
    all_fields_index = ""

    for field_object in target_field_list:

        if "FK" in field_object:
            fk_id = field_object.split("::")[1]

            for obj in eval('selected_document' + all_fields_index):
                if fk_id in obj.values():
                    all_fields_index += "[" + str(eval('selected_document' + all_fields_index).index(obj)) + "]"
        else:
            all_fields_index += "['" + field_object + "']"
        field_object_index += 1

    base_data = []
    for base_id in kwargs["base_id"]:
        base_database_fields = {"id": base_id,
                                "relation_index": kwargs["base_database"]}
        base_data.append(base_database_fields)
    exec('selected_document' + all_fields_index + '=base_data')
    update_data_to_target = DataBaseCTRL(kwargs["target_database"]).update(data=selected_document,
                                                                           id=kwargs["target_id"])

    return update_data_to_target


def append_data(data):
    document = DataBaseCTRL(data["relation_index"]).get_by_id(data["id"])
    return document


def relation_connector(data, time):
    times = time
    if type(data) != int and type(data) is not None:
        for key_one in data:
            if type(data) == str or type(data) == int:
                pass
            elif type(data) == list and len(data) > 0:
                key_two_index = 0
                for key_two in data:
                    if "relation_index" in key_two:
                        try:
                            times += 1
                            must_append_data = append_data(key_two)
                            del data[key_one][key_two_index]["id"]
                            del data[key_one][key_two_index]["relation_index"]
                            for f in must_append_data:
                                data[key_one][key_two_index][f] = must_append_data[f]
                        except:
                            data[key_one][key_two_index] = {"msg": "relation is deleted"}

                    relation_connector(data[key_two_index], times)
                    key_two_index += 1
            else:
                if type(data[key_one]) == dict:
                    if key_one == "relation_index":
                        try:
                            times += 1
                            must_append_data = append_data(data[key_one])
                            del data[key_one]["id"]
                            del data[key_one]["relation_index"]
                            for f in must_append_data:
                                data[key_one][f] = must_append_data[f]
                        except:
                            data[key_one] = {"msg": "relation is deleted"}

                    else:
                        for key_two in data[key_one]:
                            relation_connector(data[key_one], times)
                elif type(data[key_one]) == list and len(data[key_one]) > 0:
                    key_two_index = 0
                    for key_two in data[key_one]:
                        if type(key_two) == dict and "relation_index" in key_two:
                            try:
                                times += 1
                                must_append_data = append_data(key_two)
                                del data[key_one][key_two_index]["id"]
                                del data[key_one][key_two_index]["relation_index"]
                                for f in must_append_data:
                                    data[key_one][key_two_index][f] = must_append_data[f]
                            except:
                                data[key_one][key_two_index] = {"msg": "relation is deleted"}
                        relation_connector(data[key_one][key_two_index], times)
                        key_two_index += 1
        return data
