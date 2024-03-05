class HistoryLog:
    def __init__(self, image, operation_name):
        self.image = image
        self.operation_name = operation_name

    def __del__(self):
        del self.image
        del self.operation_name

