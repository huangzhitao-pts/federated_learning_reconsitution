# -*- coding: utf-8 -*-

import jwt


def decode_json(token):
    return jwt.decode(token, '4ae5', algorithm='HS256')


def encode_json(token):
    return jwt.encode(token, '4ae5', algorithm='HS256')


if __name__ == '__main__':
    # print(_md5("12345678"))
    print(encode_json({
                    "user_uid": "396c7850-5548-11eb-a9fd-3c2c30f715a7",
                    "user_name": "hzt",
                    "organization_uid": "efd32f1f-554d-11eb-a93a-3c2c30f715a7",
                    "role_id": "2"
                }))
    # print(decode_json(bytes("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g", encoding="utf-8")))
    # print(jwt.decode("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g1", '4ae5', algorithm='HS256'))
    # 25d55ad283aa400af464c76d713c07ad
