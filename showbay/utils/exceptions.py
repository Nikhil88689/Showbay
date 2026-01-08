class ExternalAPIException(Exception):
    """
    Custom exception for external API errors.
    """
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(Exception):
    """
    Custom exception for database errors.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)