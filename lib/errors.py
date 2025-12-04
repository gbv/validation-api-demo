from .validate import ValidationError  # noqa


class ApiError(Exception):
    code = 400

    def to_dict(self):
        return {
            "code": self.code,
            "message": str(self)
        }


class NotFound(ApiError):
    code = 404


class ServerError(ApiError):
    code = 500
