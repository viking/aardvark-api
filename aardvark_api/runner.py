from injector import Key, Injector, singleton
from waitress import serve

from aardvark_api.types import Configuration
from aardvark_api.application import Application
from aardvark_api.adapter import Adapter

class Runner:
    def __init__(self, **config):
        self.config = config
        self.bootstrap()

    def configure(self, binder):
        binder.bind(Configuration, to=self.config, scope=singleton)

    def bootstrap(self):
        self.injector = Injector([self.configure])
        self.app = self.injector.get(Application)
        self.adapter = self.injector.get(Adapter)

    def run(self):
        self.adapter.migrate()
        serve(self.app, host=self.config['host'], port=self.config['port'])
