import io
import re
import json
from injector import singleton, inject
from aardvark_api.controller import PackageController
from aardvark_api.types import Failure, Success, Stream, NotFound

@singleton
class Router:
    @inject
    def __init__(self, package_controller: PackageController):
        self.package_controller = package_controller
        self.routes = (
            (
                "POST",
                re.compile(r"^/packages/?$"),
                package_controller.create
            ),
            (
                "GET",
                re.compile(r"^/packages/?$"),
                package_controller.index
            ),
            (
                "GET",
                re.compile(r"^/packages/(?P<name>\w+)/(?P<version>\d+(?:[-.]\d+)*)/download$"),
                package_controller.download
            )
        )

    def route(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        status = '404 Not Found'
        headers = []
        response = []
        for route in self.routes:
            if route[0] != method:
                continue

            md = route[1].match(path)
            if md is None:
                continue

            result = route[2](md.groupdict(), environ, start_response)

            if isinstance(result, Success):
                status = '200 OK'
                headers.append(('Content-Type', 'application/json'))
                response.append(bytes(json.dumps(result), 'utf-8'))

            elif isinstance(result, Failure):
                status = '400 Bad Request'
                headers.append(('Content-Type', 'application/json'))
                response.append(bytes(json.dumps(result), 'utf-8'))

            elif isinstance(result, NotFound):
                status = '404 Not Found'

            elif isinstance(result, Stream):
                status = '200 OK'
                headers.extend((
                    ('Content-Type', result.mime_type),
                    ('Content-Disposition', f"attachment; filename=\"{result.filename}\"")
                ))
                if 'wsgi.file_wrapper' in environ:
                    response = environ['wsgi.file_wrapper'](result.stream, 8192)
                else:
                    response = iter(lambda: result.stream.read(8192), '')
            break

        start_response(status, headers)
        return response
