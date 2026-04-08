class SyncRunNotImplemented(NotImplementedError):
    def __init__(self):
        super().__init__("Synchronous execution is not supported. Use the async variant.")
