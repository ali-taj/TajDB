def pagination():
    size = 50

    pages = 200 // size
    if 200 % size > 0:
        pages += 1


def relation_controller(**kwargs):
    # relation_document = {
    #     "target_index": ,
    #     "target_field": ,  # "field1.object.object"
    #     "target_id": ,
    #     "base_index": ,
    #     "base_id":  # ["field1", "field2.object"]
    # }

    target_field_list = kwargs['target_field'].split(".")
    field_object_index = 0
    all_fields_index = ""

    selected_document = selected_elastic.get(index=kwargs["target_index"], id=kwargs["target_id"])["_source"]

    for field_object in target_field_list:

        if "FK" in field_object:
            fk_id = field_object.split("::")[1]

            for obj in eval('selected_document' + all_fields_index):
                if fk_id in obj.values():
                    all_fields_index += "[" + str(eval('selected_document' + all_fields_index).index(obj)) + "]"
        else:
            all_fields_index += "['" + field_object + "']"
        field_object_index += 1

    if kwargs["base_index"] == "dataset":
        base_data = []
        for base_id in kwargs["base_id"]:
            base_index_fields = {"id": base_id,
                                 "relation_index": kwargs["base_index"],
                                 "labels": kwargs["base_id"][base_id]}
            base_data.append(base_index_fields)

    else:
        base_data = []
        for base_id in kwargs["base_id"]:
            base_index_fields = {"id": base_id,
                                 "relation_index": kwargs["base_index"]}
            base_data.append(base_index_fields)
    exec('selected_document' + all_fields_index + '=base_data')
    update_data_to_target = selected_elastic.index(index=kwargs["target_index"], id=kwargs["target_id"],
                                                   document=selected_document)

    return update_data_to_target


def append_data(data):
    document = target_elasticsearch.get(index=data["relation_index"], id=data["id"])
    del document["_index"]
    del document["found"]
    del document["_seq_no"]
    del document["_primary_term"]
    del document["_version"]

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
