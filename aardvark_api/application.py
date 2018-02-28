from injector import inject
from aardvark_api.router import Router

class Application:
    @inject
    def __init__(self, router: Router):
        self.router = router

    def __call__(self, environ, start_response):
        return self.router.route(environ, start_response)
