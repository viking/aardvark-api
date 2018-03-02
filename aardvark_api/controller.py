import json
from injector import singleton, inject
from aardvark_api.action import CreatePackage, ListPackages, SearchPackages, DownloadPackage
from aardvark_api.types import Failure

class PackageController:
    @inject
    def __init__(self, create: CreatePackage, index: ListPackages,
            search: SearchPackages, download: DownloadPackage):
        self._create = create
        self._index = index
        self._search = search
        self._download = download

    def create(self, params, environ, start_response) -> dict:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        return self._create.run(environ['wsgi.input'], request_body_size)

    def index(self, params, environ, start_response) -> dict:
        return self._index.run(conditions)

    def search(self, params, environ, start_response) -> dict:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        conditions = None
        if request_body_size > 0:
            if environ.get('CONTENT_TYPE') != 'application/json':
                return Failure(error = "Invalid content type")

            try:
                conditions = json.loads(environ['wsgi.input'].read())
            except (json.JSONDecodeError):
                return Failure(error = "Invalid JSON input")

        return self._search.run(conditions)

    def download(self, params, environ, start_response) -> dict:
        return self._download.run(params['name'], params['version'])
