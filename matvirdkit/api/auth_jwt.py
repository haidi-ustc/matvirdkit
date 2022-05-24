from datetime import datetime,timedelta
from typing import Dict

import jwt
from decouple import config

JWT_SECRET = config("TOKEN_SALT")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {
        "access_token": token
    }


def generate_access_token(username: str,exp :float = 2) -> Dict[str, str]:
    """
    生成access_token
    :param username: 用户名(自定义部分)
    :param algorithm: 加密算法
    :param exp: 过期时间
    :return:token
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=exp)
    payload = {
            "iss": "materialDB",
            "iat": now,
            # "flag": 0, #是否为一次性token 0是，1不是
            "username": username,
            "exp": expire,
            "jti": ""
        }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_auth_token(token: str) -> dict:
    """
    解密token
    :param token:token字符串
    :return:
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except:
        return {}

def identify(token: str):
    """
    用户鉴权
    """

    if token:
        payload = decode_auth_token(token)
        if not payload:
            return False
        if "username" in payload:
            return True
        # if "username" in payload and "flag" in payload:
        #     if payload["flag"] == 0:
        #         return payload["username"]
        #     else:
        #         return False
    return False

def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
