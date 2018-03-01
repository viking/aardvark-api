import re
import tarfile
import typing
from injector import inject
from rpy2.robjects.packages import importr
from rpy2.rinterface import RRuntimeError

from aardvark_api.exceptions import InvalidPackageError

class Package:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.version = kwargs.get('version', None)
        self.dependencies = kwargs.get('dependencies', None)
        self.filename = kwargs.get('filename', None)

class PackageFactory:
    @inject
    def __init__(self):
        self.r_base = importr('base')

    def from_tarball(self, filename) -> Package:
        # make sure file is a tarball
        if not tarfile.is_tarfile(filename):
            raise InvalidPackageError('The file is not a tarball.')

        # check for DESCRIPTION file
        tf = tarfile.open(filename, "r:gz")
        try:
            package_name = None
            tf_contents = []
            for name in tf.getnames():
                parts = name.split('/', maxsplit=1)

                dirname = parts[0]
                if package_name is None:
                    package_name = dirname
                elif package_name != dirname:
                    raise InvalidPackageError('The tarball does not have the correct directory structure.')

                if len(parts) > 1:
                    if parts[1] in tf_contents:
                        raise InvalidPackageError('The tarball has duplicate files.')

                    tf_contents.append(parts[1])

            if not 'DESCRIPTION' in tf_contents:
                raise InvalidPackageError('The tarball does not have a DESCRIPTION file.')

            # extract DESCRIPTION file and parse with R
            desc_data = tf.extractfile(f"{package_name}/DESCRIPTION").read()
            desc_str = desc_data.decode("utf-8")
            package = self.parse_description(desc_str)

            if package.name != package_name:
                raise InvalidPackageError('The tarball does not have the correct directory structure.')

            return package
        finally:
            tf.close()

    def is_valid_version(self, version: str) -> bool:
        try:
            numeric_version = self.r_base.numeric_version(version)
            return True
        except RRuntimeError as err:
            return False

    def parse_description(self, desc: str) -> Package:
        desc_conn = self.r_base.textConnection(desc)
        desc_dcf = self.r_base.read_dcf(desc_conn)
        self.r_base.close(desc_conn)
        values = dict(zip(desc_dcf.colnames, desc_dcf))

        result = dict()
        # check package name
        if not 'Package' in values:
            raise InvalidPackageError("DESCRIPTION file does not contain a package name.")
        package_name = values['Package']

        # check package version
        if not 'Version' in values:
            raise InvalidPackageError("DESCRIPTION file does not contain a package version.")
        if not self.is_valid_version(values['Version']):
            raise InvalidPackageError("DESCRIPTION file contains invalid package version.")
        package_version = values['Version']

        # check package dependencies
        package_deps = []
        if 'Depends' in values:
            for dep in re.split(r"\s*,\s*", values['Depends']):
                m = re.match(r"^(?P<name>\w+)(?:\s*\((?P<op>>=?|<=?|!?=)\s*(?P<version>[^)]+)\))?$", dep)
                if m is None:
                    raise InvalidPackageError("DESCRIPTION file contains invalid package dependencies.")

                dep_version = m.group('version')
                if not dep_version is None:
                    if not self.is_valid_version(dep_version):
                        raise InvalidPackageError("DESCRIPTION file contains invalid package dependencies.")

                package_deps.append({
                    'name': m.group('name'),
                    'operator': m.group('op'),
                    'version': dep_version
                })

        return Package(
            name = package_name,
            version = package_version,
            dependencies = package_deps)
