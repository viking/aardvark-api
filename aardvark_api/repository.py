import typing
import json
from injector import singleton, inject
from aardvark_api.adapter import Adapter
from aardvark_api.package import Package

@singleton
class PackageRepository:
    @inject
    def __init__(self, adapter: Adapter):
        self.adapter = adapter

    def create(self, package: Package) -> Package:
        values = {
            'name': package.name,
            'version': package.version,
            'dependencies': json.dumps(package.dependencies),
            'filename': package.filename
        }
        record_id = self.adapter.create("packages", values)
        package.id = record_id
        return package

    def find(self, conditions=None) -> typing.List[Package]:
        result = []
        for values in self.adapter.find("packages", conditions):
            values['dependencies'] = json.loads(values['dependencies'])
            result.append(Package(**values))
        return result
