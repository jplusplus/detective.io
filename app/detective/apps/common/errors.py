class MalformedRequestError(KeyError):
    pass

class ForbiddenError(StandardError):
    pass

class UnauthorizedError(StandardError): 
    pass