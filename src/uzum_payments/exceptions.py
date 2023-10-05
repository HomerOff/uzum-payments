class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    pass


class UzumCheckoutException(Exception):
    def __init__(self, message: dict, code: int = None):
        self.message = message.get('message') or message
        self.code = code

class NotResponding(ApiError):
    """Raised if the API request timed out"""
    def __init__(self):
        self.code = 504
        self.error = 'API request timed out, please be patient.'
        super().__init__(self.error, self.code)


class NetworkError(ApiError):
    """Raised if there is an issue with the network
    (i.e. aiohttp.ServerDisconnectedError or requests.ConnectionError)
    """
    def __init__(self):
        self.code = 503
        self.error = 'Network down.'
        super().__init__(self.error, self.code)


class InternalError(UzumCheckoutException):
    pass


class PaymentErrors(UzumCheckoutException):
    pass


class ValidationError(UzumCheckoutException):
    pass

class AuthenticationError(UzumCheckoutException):
    pass


class BadRequest(UzumCheckoutException):
    pass

class SignatureError(UzumCheckoutException):
    pass

class FingerprintError(UzumCheckoutException):
    pass

class InternalServerError(UzumCheckoutException):
    pass

class UnexpectedError(UzumCheckoutException):
    """Raised if the error was not caught"""
    pass