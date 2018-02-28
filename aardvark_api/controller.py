from injector import singleton, inject
from aardvark_api.action import CreatePackage, ListPackages

class PackageController:
    @inject
    def __init__(self, create: CreatePackage, index: ListPackages):
        self._create = create
        self._index = index

    def create(self, environ, start_response) -> dict:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        return self._create.run(environ['wsgi.input'], request_body_size)

    def index(self, environ, start_response) -> dict:
        return self._index.run()
