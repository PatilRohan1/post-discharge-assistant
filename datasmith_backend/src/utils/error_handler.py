from fastapi.responses import JSONResponse
from src.api.custom_exception import CustomException
from src.constants.http_constants import HttpConstant
import asyncpg
from pydantic import ValidationError
import jwt
from jwt.exceptions import ExpiredSignatureError


def error_handler(exception: Exception):
    if isinstance(exception, CustomException):
        return JSONResponse(
            status_code=exception.status_code,
            content={"message": exception.message, "error": exception.error},
        )

    elif isinstance(exception, ValidationError):
        errors = []
        for error in exception.errors():
            errors.append(
                {
                    "field": error.get("loc", ["unknown"])[-1],
                    "message": error.get("msg"),
                }
            )
        return JSONResponse(
            status_code=422,
            content={"errors": errors},
        )

    elif isinstance(exception, ExpiredSignatureError):
        return JSONResponse(
            status_code=HttpConstant.UNAUTHORIZED.value,
            content={"message": "Token has expired. Please request a new token.", "error": str(exception)},
        )

    elif isinstance(exception, asyncpg.exceptions.PostgresError):
        return JSONResponse(
            status_code=HttpConstant.INTERNAL_SERVER_ERROR.value,
            content={
                "message": f"Internal database error occurred while processing the request.",
                "error": str(exception),
            },
        )

    else:
        return JSONResponse(
            status_code=HttpConstant.INTERNAL_SERVER_ERROR.value,
            content={
                "message": f"An unhandled exception occurred during API execution",
                "error": str(exception),
            },
        )
