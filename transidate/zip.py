import zipfile

from transidate.validators import TransXChangeValidator
from transidate.xsd import XSDConfig, XSDDownloader


class ZipValidator:
    def __init__(self, file):
        self._file = file
        self._schemas = {}
        self._zip = zipfile.ZipFile(self._file)

    def get_schema(self, conf: XSDConfig):
        schema = self._schemas.get(conf.url, None)

        if schema is None:
            downloader = XSDDownloader.from_xsd_config(conf)
            schema = downloader.download_xsd()
            self._schemas[conf.url] = schema
        return schema

    def get_filenames(self):
        return [name for name in self._zip.namelist() if name.endswith("xml")]

    def get_validator_by_name(self, name):
        with self._zip.open(name) as f_:
            return TransXChangeValidator(f_)

    def validate_files(self):
        names = self.get_filenames()
        for name in names:
            validator = self.get_validator_by_name(name)
            conf = validator.get_config()
            schema = self.get_schema(conf)
            result = validator.validate(schema)
            yield result
