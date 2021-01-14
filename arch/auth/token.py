# -*- coding: utf-8 -*-

import jwt


def decode_json(token):
    return jwt.decode(token, '4ae5', algorithm='HS256')


def encode_json(token):
    return jwt.encode(token, '4ae5', algorithm='HS256')


if __name__ == '__main__':
    # print(_md5("12345678"))
    print(encode_json({
                    "user_uid": "78217c8b-562e-11eb-97b7-3c2c30f715a7",
                    "user_name": "hzt",
                    "organization_uid": "78215597-562e-11eb-9542-3c2c30f715a7",
                    "role_id": "2"
                }))
    # eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3VpZCI6Ijc4MjE3YzhiLTU2MmUtMTFlYi05N2I3LTNjMmMzMGY3MTVhNyIsInVzZXJfbmFtZSI6Imh6dCIsIm9yZ2FuaXphdGlvbl91aWQiOiI3ODIxNTU5Ny01NjJlLTExZWItOTU0Mi0zYzJjMzBmNzE1YTciLCJyb2xlX2lkIjoiMiJ9.yOk3ugR31nZeRNnEdZE7aIyJAuzYxB5Q9b2I6ob5f7I
    print(encode_json({
                    "user_uid": "7849d1d1-562e-11eb-8262-3c2c30f715a7",
                    "user_name": "zy",
                    "organization_uid": "78217c8a-562e-11eb-abdd-3c2c30f715a7",
                    "role_id": "2"
                }))
    # eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3VpZCI6Ijc4NDlkMWQxLTU2MmUtMTFlYi04MjYyLTNjMmMzMGY3MTVhNyIsInVzZXJfbmFtZSI6Inp5Iiwib3JnYW5pemF0aW9uX3VpZCI6Ijc4MjE3YzhhLTU2MmUtMTFlYi1hYmRkLTNjMmMzMGY3MTVhNyIsInJvbGVfaWQiOiIyIn0.gDIgpiJqlvMkuVxcKZfqao_BLwYl8k2DIESNY4nFP_M

    # print(decode_json(bytes("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g", encoding="utf-8")))
    # print(jwt.decode("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g1", '4ae5', algorithm='HS256'))
    # 25d55ad283aa400af464c76d713c07ad
