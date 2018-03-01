from injector import inject, singleton
from aardvark_api.types import Configuration
from aardvark_api.package import Package

@singleton
class UrlBuilder:
    @inject
    def __init__(self, config: Configuration):
        self.config = config

    def package_url(self, package: Package) -> str:
        port = ""
        if self.config['port'] != 80:
            port = f":{self.config['port']}"
        return "http://{}{}/packages/{}_{}.tar.gz".format(self.config['host'],
            port, package.name, package.version)

