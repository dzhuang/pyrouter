class RouterNotCompatible(Exception):
    pass


class ValidationError(Exception):
    pass


class DeviceNotFound(Exception):
    pass


class RequestError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class RouterAPIError(Exception):
    pass
