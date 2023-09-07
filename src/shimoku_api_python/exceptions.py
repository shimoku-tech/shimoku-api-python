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


class BoardError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class MenuPathError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class WorkspaceError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class ActivityError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class ActivityTemplateError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class AIFunctionError(Exception):
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code
        

class ShimokuFileError(Exception):
    
    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code


class UniverseApiKeyError(Exception):

    def __init__(self, text, status_code=None):
        self.text = text
        self.status_code = status_code
