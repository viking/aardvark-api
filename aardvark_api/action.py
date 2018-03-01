import os
import shutil
import typing
from tempfile import TemporaryDirectory
from injector import singleton, inject

from aardvark_api.repository import PackageRepository
from aardvark_api.types import Configuration, Success, Failure, Stream, NotFound
from aardvark_api.exceptions import IntegrityError, InvalidPackageError
from aardvark_api.package import Package, PackageFactory
from aardvark_api.util import UrlBuilder

@singleton
class CreatePackage:
    @inject
    def __init__(self, config: Configuration, repo: PackageRepository,
            factory: PackageFactory, url_builder: UrlBuilder):
        self.config = config
        self.repo = repo
        self.factory = factory
        self.url_builder = url_builder

    def run(self, stream, length) -> dict:
        tmpdir = TemporaryDirectory()
        upload_filename = os.path.join(tmpdir.name, "package")
        with open(upload_filename, 'wb') as f:
            pos = 0
            while pos < length:
                amount = 8192
                if amount > (length - pos):
                    amount = length - pos
                f.write(stream.read(amount))
                pos += amount

        try:
            package = self.factory.from_tarball(upload_filename)
        except InvalidPackageError as err:
            tmpdir.cleanup()
            return Failure(file = str(err))

        package.filename = os.path.join(
            self.config["package_path"],
            f"{package.name}_{package.version}.tar.gz")
        shutil.copy(upload_filename, package.filename)

        try:
            package = self.repo.create(package)
            return Success(
                name = package.name,
                version = package.version,
                dependencies = package.dependencies,
                url = self.url_builder.package_url(package))

        except IntegrityError as error:
            os.remove(package.filename)
            return Failure(file = f"{package.name} version {package.version} has already been submitted.")

        finally:
            tmpdir.cleanup()

@singleton
class ListPackages:
    @inject
    def __init__(self, repo: PackageRepository, url_builder: UrlBuilder):
        self.repo = repo
        self.url_builder = url_builder

    def process(self, packages: typing.List[Package]) -> typing.List[dict]:
        result = [{
            'name': package.name,
            'version': package.version,
            'dependencies': package.dependencies,
            'url': self.url_builder.package_url(package)
        } for package in packages]
        return Success(packages = result)

    def run(self) -> dict:
        packages = self.repo.find()
        return self.process(packages)

@singleton
class SearchPackages(ListPackages):
    def run(self, conditions) -> dict:
        if not conditions is None:
            if not isinstance(conditions, dict):
                return Failure(conditions = "must be an object")

            expected_keys = {"name", "version"}
            keys = set(conditions.keys())
            if len(keys - expected_keys) > 0:
                return Failure(conditions = "contain invalid keys")

        packages = self.repo.find(conditions)
        return self.process(packages)

@singleton
class DownloadPackage:
    @inject
    def __init__(self, repo: PackageRepository):
        self.repo = repo

    def run(self, name: str, version: str) -> dict:
        packages = self.repo.find(dict(name = name, version = version))
        if len(packages) == 0:
            return NotFound()

        package = packages[0]
        filename = package.filename
        return Stream(
            stream = open(filename, 'rb'),
            size = os.path.getsize(filename),
            filename = f"{package.name}_{package.version}.tar.gz",
            mime_type = "application/x-gzip")
