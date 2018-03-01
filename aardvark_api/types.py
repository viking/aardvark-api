from injector import Key

Configuration = Key('configuration')

class Failure(dict):
    pass

class Success(dict):
    pass

class NotFound:
    pass

class Stream:
    def __init__(self, stream, size, filename, mime_type):
        self.stream = stream
        self.size = size
        self.filename = filename
        self.mime_type = mime_type
