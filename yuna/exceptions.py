

class YunaException(Exception):
    pass


class SourceError(YunaException):
    pass


class DestinationRefuseError(YunaException):
    pass


class CreateError(YunaException):
    pass


class SettingError(YunaException):
    pass


SetiingError = SettingError