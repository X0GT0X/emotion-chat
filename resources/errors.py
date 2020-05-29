class InternalServerError(Exception):
    pass


class SchemaValidationError(Exception):
    pass


class LoginAlreadyExistsError(Exception):
    pass


class UnauthorizedError(Exception):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
     "SchemaValidationError": {
         "message": "Request is missing required fields",
         "status": 400
     },
     "LoginAlreadyExistsError": {
         "message": "User with given login already exists",
         "status": 400
     },
     "UnauthorizedError": {
         "message": "Invalid login or password",
         "status": 401
     }
}