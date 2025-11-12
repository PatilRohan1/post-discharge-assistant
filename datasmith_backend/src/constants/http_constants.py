from enum import Enum


class HttpConstant(int, Enum):
    OK = 200
    SUCCESS_CREATE = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    CONFLICT = 409
    INVALID_TOKEN = 498
