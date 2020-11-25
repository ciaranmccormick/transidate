from pathlib import Path

import pytest
from transidate.exceptions import NotSupported
from transidate.xsd import (
    Config,
    DownloaderFactory,
    XMLDownloader,
    ZipDownloader,
    get_xsd,
)


class TestGetXSD:
    def test_get_xsd_exception(self):
        source = "blah"

        with pytest.raises(NotSupported) as exc:
            get_xsd(source)
            assert "'source' is not a valid XMLSource." in str(exc.value)


class TestDowloadFactory:
    def test_get_xml_downloader(self):
        url = "http://axmlurl.zz/schema.xsd"
        root = Path("TransXChange_general.xsd")
        config = Config(url, root)
        factory = DownloaderFactory(config)
        downloader = factory.get_downloader()
        assert isinstance(downloader, XMLDownloader)

    def test_get_zip_downloader(self):
        url = "http://axmlurl.zz/schema.zip"
        root = Path("TransXChange_general.xsd")
        config = Config(url, root)
        factory = DownloaderFactory(config)
        downloader = factory.get_downloader()
        assert isinstance(downloader, ZipDownloader)
