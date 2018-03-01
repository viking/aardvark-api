from injector import singleton, inject
from aardvark_api.action import CreatePackage, ListPackages, DownloadPackage

class PackageController:
    @inject
    def __init__(self, create: CreatePackage, index: ListPackages, download: DownloadPackage):
        self._create = create
        self._index = index
        self._download = download

    def create(self, params, environ, start_response) -> dict:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        return self._create.run(environ['wsgi.input'], request_body_size)

    def index(self, params, environ, start_response) -> dict:
        return self._index.run()

    def download(self, params, environ, start_response) -> dict:
        return self._download.run(params['name'], params['version'])
