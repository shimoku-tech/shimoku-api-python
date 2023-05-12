""""""


class ApiClientError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class ResourceIdMissing(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class CacheError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class TabsError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class ModalError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class DataError(Exception):

    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code