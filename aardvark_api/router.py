import re
import json
from injector import singleton, inject
from aardvark_api.controller import PackageController
from aardvark_api.types import Failure, Success

@singleton
class Router:
    @inject
    def __init__(self, package_controller: PackageController):
        self.package_controller = package_controller
        self.routes = (
            ("POST", re.compile("^/packages/?$"), package_controller.create),
            ("GET", re.compile("^/packages/?$"), package_controller.index),
        )

    def route(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        status = '404 Not Found'
        headers = []
        response = []
        for route in self.routes:
            if route[0] == method and route[1].match(path):
                result = route[2](environ, start_response)
                if isinstance(result, Success):
                    status = '200 OK'
                else:
                    status = '400 Bad Request'

                headers.append(('Content-Type', 'application/json'))
                response.append(bytes(json.dumps(result), 'utf-8'))
                break

        start_response(status, headers)
        return response
