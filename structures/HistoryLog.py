class HistoryLog:
    def __init__(self, image, operation_name, layer):
        self.image = image
        self.operation_name = operation_name
        self.layer = layer

    def __del__(self):
        del self.image
        del self.operation_name
        del self.layer
