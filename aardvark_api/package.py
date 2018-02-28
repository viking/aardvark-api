import re
import tarfile
from rpy2.robjects.packages import importr

from aardvark_api.exceptions import InvalidPackageError

class Package:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.version = kwargs.get('version', None)
        self.filename = kwargs.get('filename', None)

class PackageProcessor:
    def tarball(self, filename) -> Package:
        # make sure file is a tarball
        if not tarfile.is_tarfile(filename):
            raise InvalidPackageError('The file is not a tarball.')

        # check for DESCRIPTION file
        tf = tarfile.open(filename)
        try:
            package_name = None
            tf_contents = []
            for name in tf.getnames():
                parts = name.split('/', maxsplit=1)
                if len(parts) == 1:
                    raise InvalidPackageError('The tarball does not have the correct directory structure.')

                dirname = parts[0]
                if package_name is None:
                    package_name = dirname
                elif package_name != dirname:
                    raise InvalidPackageError('The tarball does not have the correct directory structure.')

                if parts[1] in tf_contents:
                    raise InvalidPackageError('The tarball has duplicate files.')

                tf_contents.append(parts[1])

            if not 'DESCRIPTION' in tf_contents:
                raise InvalidPackageError('The tarball does not have a DESCRIPTION file.')

            # extract DESCRIPTION file and parse with R
            desc_data = tf.extractfile(f"{package_name}/DESCRIPTION").read()

            r_base = importr('base')
            desc_conn = r_base.textConnection(desc_data.decode("utf-8"))
            desc_dcf = r_base.read_dcf(desc_conn)
            r_base.close(desc_conn)

            values = dict(zip(desc_dcf.colnames, desc_dcf))
            if values['Package'] != package_name:
                raise InvalidPackageError('The tarball does not have the correct directory structure.')

            version_pattern = re.compile("^\d+([.-]\d+)+$")
            package_version = values['Version']
            if not type(package_version) is str or not version_pattern.match(values['Version']):
                raise InvalidPackageError('The version string in the DESCRIPTION file is invalid.')

            return Package(name = package_name, version = package_version)
        finally:
            tf.close()
