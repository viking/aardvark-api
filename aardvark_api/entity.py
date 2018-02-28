class Package:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.version = kwargs.get('version', None)
        self.filename = kwargs.get('filename', None)
