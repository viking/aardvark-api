from injector import Key

Configuration = Key('configuration')

class Failure(dict):
    pass

class Success(dict):
    pass

class IntegrityError(Exception):
    pass
