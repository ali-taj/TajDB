import datetime

import jwt
from django.conf import settings


def authentication(request):
    valid_urls = ["hashtag_manage", "post", "message", "instagram_user", "hashtag_to_post", "last_data", "insta_user",
                  "account_category", "account_scenario", "account_message", "labels", "dataset", "label", "company",
                  "post", "dataset_category", "pre_register", "register", "apk-download", "get_user", "get_missions",
                  "create_missions", "run_missions", "filter-user", "execute_mission", "user_manage", "classes",
                  "category", "command", "tier", "tier_title"]

    authCode = request.META.get("HTTP_AUTHORIZATION", 0).split(" ")[1]
    # token_find = ModelLogin.objects.filter(access_token=authCode).count()
    token_find = 2
    if token_find == 1:
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
            # user_type = Elastic.search(Elastic, index='user', search_type={"type": "id",
            #                                                                "data": user_id})['type']
            # permissions = Elastic.search(Elastic, index='user_permissions',
            #                              search_type={"type": "body", "data": {"query": {"match_phrase": {
            #                                  "name": user_type}}}})['items'][0]['_source']
            user_type = 1
            permissions = "test"

            if permissions["name"] == "admin":
                return "True"
            else:
                url_split = request.path.split('/')
                url_index = 0
                for obj in url_split:
                    if obj in valid_urls:
                        url = url_split[url_index]
                    url_index -= 1
                method = request.method
                auth_403 = 0
                auth = 403
                for permission_url in permissions['urls']:
                    if url == permission_url:
                        for permission_method in permissions['urls'][permission_url]:
                            if method == permission_method:
                                if permissions['urls'][permission_url][permission_method] == "all":
                                    auth = 200
                                else:
                                    for query_object in permissions['urls'][permission_url][permission_method]:
                                        key = \
                                            list(permissions['urls'][permission_url][permission_method][query_object])[
                                                0]
                                        value = permissions['urls'][permission_url][permission_method][query_object][
                                            key]

                                        auth = {"query": {query_object: {key: {"value": value}}}}
                                pass
                            else:
                                auth_403 += 1

                    else:
                        auth_403 += 1
                if auth_403 > 0:
                    auth = 403 if auth_403 == len(permissions['urls']) else 200
                if auth == 403:
                    return Response({"error": "you don't have permissions for this request!"},
                                    status=status.HTTP_403_FORBIDDEN)
                elif auth == 200:
                    return "True"
                else:
                    return auth
    else:
        return Response({"error": "auth failed"}, status=status.HTTP_401_UNAUTHORIZED)