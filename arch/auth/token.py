# -*- coding: utf-8 -*-

import jwt


def decode_json(token):
    return jwt.decode(token, '4ae5', algorithm='HS256')


def encode_json(token):
    return jwt.encode(token, '4ae5', algorithm='HS256')


if __name__ == '__main__':
    # print(_md5("12345678"))
    print(encode_json({
                    "user_uid": "6346b26b-5930-11eb-8ed2-3c2c30f715a7",
                    "user_name": "hzt",
                    "organization_uid": "6346b268-5930-11eb-a743-3c2c30f715a7",
                    "role_id": "2"
                }))
    # eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3VpZCI6IjYzNDZiMjZiLTU5MzAtMTFlYi04ZWQyLTNjMmMzMGY3MTVhNyIsInVzZXJfbmFtZSI6Imh6dCIsIm9yZ2FuaXphdGlvbl91aWQiOiI2MzQ2YjI2OC01OTMwLTExZWItYTc0My0zYzJjMzBmNzE1YTciLCJyb2xlX2lkIjoiMiJ9.UC_paQbnbUT67gy3Hu-YPgwolutOywAil6zw3CGp5sc
    print(encode_json({
                    "user_uid": "635fa797-5930-11eb-8110-3c2c30f715a7",
                    "user_name": "zy",
                    "organization_uid": "6346b269-5930-11eb-8f10-3c2c30f715a7",
                    "role_id": "2"
                }))
    # eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3VpZCI6IjYzNWZhNzk3LTU5MzAtMTFlYi04MTEwLTNjMmMzMGY3MTVhNyIsInVzZXJfbmFtZSI6Inp5Iiwib3JnYW5pemF0aW9uX3VpZCI6IjYzNDZiMjY5LTU5MzAtMTFlYi04ZjEwLTNjMmMzMGY3MTVhNyIsInJvbGVfaWQiOiIyIn0.huyH0XI9l_zil4Z69jx1-jDhiVyUr25ypAPJ7WX4hK0

    # print(decode_json(bytes("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g", encoding="utf-8")))
    # print(jwt.decode("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g1", '4ae5', algorithm='HS256'))
    # 25d55ad283aa400af464c76d713c07ad
