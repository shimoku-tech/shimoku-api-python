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


class TableError(Exception):
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


class FileError(Exception):

    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class BentoboxError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class DashboardError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class AppError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class BusinessError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code

