import os
import re
import shutil
import tarfile
from tempfile import TemporaryDirectory
from injector import singleton, inject
from rpy2.robjects.packages import importr

from aardvark_api.repository import PackageRepository
from aardvark_api.types import Configuration, Success, Failure, IntegrityError
from aardvark_api.entity import Package

@singleton
class CreatePackage:
    @inject
    def __init__(self, config: Configuration, repo: PackageRepository):
        self.config = config
        self.repo = repo

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

        # make sure file is a tarball
        if not tarfile.is_tarfile(upload_filename):
            return Failure(file = 'The file must be a tarball.')

        # check for DESCRIPTION file
        tf = tarfile.open(upload_filename)
        package_name = None
        tf_contents = []
        try:
            for name in tf.getnames():
                parts = name.split('/', maxsplit=1)
                if len(parts) == 1:
                    return Failure(file = 'The tarball does not have the correct directory structure.')

                dirname = parts[0]
                if package_name is None:
                    package_name = dirname
                elif package_name != dirname:
                    return Failure(file = 'The tarball does not have the correct directory structure.')

                if parts[1] in tf_contents:
                    return Failure(file = 'The tarball has duplicate files.')

                tf_contents.append(parts[1])

            if not 'DESCRIPTION' in tf_contents:
                return Failure(file = 'The tarball does not have a DESCRIPTION file.')

            # extract DESCRIPTION file and parse
            tf.extract('{}/DESCRIPTION'.format(package_name), tmpdir.name)
            desc_filename = os.path.join(tmpdir.name, package_name, "DESCRIPTION")

            base = importr('base')
            dcf = base.read_dcf(desc_filename)
            desc = dict(zip(dcf.colnames, dcf))
            if desc['Package'] != package_name:
                return Failure(file = 'The tarball does not have the correct directory structure.')

            version_pattern = re.compile("^\d+([.-]\d+)+$")
            package_version = desc['Version']
            if not type(package_version) is str or not version_pattern.match(desc['Version']):
                return Failure(file = 'The version string in the DESCRIPTION file is invalid.')

            package_filename = f"{package_name}-{package_version}.tar"
            package_filename = os.path.join(self.config["package_path"], package_filename)
            shutil.copy(upload_filename, package_filename)

            package = Package(
                name = package_name,
                version = package_version,
                filename = package_filename)

            try:
                package = self.repo.create(package)
                return Success(name = package.name, version = package.version)

            except IntegrityError as error:
                os.remove(package_filename)
                return Failure(file = f"{package.name} version {package.version} has already been submitted.")

        finally:
            tf.close()
            tmpdir.cleanup()
