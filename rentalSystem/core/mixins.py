class ServiceResult:
    def __init__(self, success: bool, data=None, error: str | None = None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data=None):
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str):
        return cls(False, error=error)
