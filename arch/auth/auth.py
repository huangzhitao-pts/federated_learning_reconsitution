from .token import decode_json
from functools import wraps
from flask import request, g, abort


def login_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        authorization = request.headers.get("Authorization")
        if authorization:
            token = authorization.split()[-1]
            try:
                """
                {
                    "user_uid": String,
                    "user_name": String,
                    "organization_uid": String,
                    "role_id": String
                }
                """
                g.token = decode_json(token)
                return view_func(*args, **kwargs)
            except Exception as e:
                print(e)
                print("authentication failure")
        return abort(404)
    return decorated_function


# def permission(view_func):
#     @wraps(view_func)
#     def decorated_function(*args, **kwargs):
#         authorization = request.headers.get("Authorization")
#         if authorization:
#             token = authorization.split()[-1]
#             # try:
#             """
#             {
#                 "user_id": String,
#                 "organization_id": String
#             }
#             """
#             g.token = decode_json(token)
#             g.token["user_id"]
#             return view_func(*args, **kwargs)
#             # except Exception as e:
#             #     print(e)
#         return abort(403)
#     return decorated_function