"""
Contains exceptions thrown by the library
"""


class ModelNotFoundError(Exception):
    """Error indicating a missing model"""


class UnsupportedModelOperationError(Exception):
    """Error indicating an operation on a model is unsupported"""
    pass
