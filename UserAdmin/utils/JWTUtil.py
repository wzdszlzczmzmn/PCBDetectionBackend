import jwt
import datetime
from PCBDetectionBackend.settings import SECRET_KEY


def generate_jwt(user):
    payload = {
        'id': str(user.UUID),
        'deviceUUID': user.deviceUUID,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, audience="HS256")

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
