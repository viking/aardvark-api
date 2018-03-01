import os
import shutil
from tempfile import TemporaryDirectory
from injector import singleton, inject

from aardvark_api.repository import PackageRepository
from aardvark_api.types import Configuration, Success, Failure, Stream, NotFound
from aardvark_api.exceptions import IntegrityError, InvalidPackageError
from aardvark_api.package import PackageFactory

@singleton
class CreatePackage:
    @inject
    def __init__(self, config: Configuration, repo: PackageRepository, factory: PackageFactory):
        self.config = config
        self.repo = repo
        self.factory = factory

    def run(self, stream, length) -> dict:
        tmpdir = TemporaryDirectory()
        upload_filename = os.path.join(tmpdir.name, "package")
        with open(upload_filename, 'wb') as f:
            pos = 0
            while pos < length:
                amount = 4096
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
                dependencies = package.dependencies)

        except IntegrityError as error:
            os.remove(package.filename)
            return Failure(file = f"{package.name} version {package.version} has already been submitted.")

        finally:
            tmpdir.cleanup()

@singleton
class ListPackages:
    @inject
    def __init__(self, repo: PackageRepository):
        self.repo = repo

    def run(self) -> dict:
        packages = self.repo.find()
        packages = [{
            'name': package.name,
            'version': package.version,
            'dependencies': package.dependencies
        } for package in packages]
        return Success(packages = packages)

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
