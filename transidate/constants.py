from typing import Final

NAPTAN_URL = "http://naptan.dft.gov.uk/transxchange/schema/"
SIRI_URL = "https://www.siri.org.uk/schema/"
NETEX_URL = "http://netex.uk/netex/schema/"

TXC_ROOT: Final = "TransXChange_general.xsd"
TXC_BASE_URL = NAPTAN_URL + "{0}/TransXChange_schema_{0}.zip"
TXC21_URL: Final = TXC_BASE_URL.format("2.1")
TXC24_URL: Final = TXC_BASE_URL.format("2.4")

SIRI_ROOT: Final = "siri.xsd"
SIRI10_URL: Final = SIRI_URL + "1.0/siri-1.0.zip"
SIRI13_URL: Final = SIRI_URL + "1.3/siri-1.3.zip"
SIRI14_URL: Final = SIRI_URL + "1.4/siri-1.4.zip"
SIRI20_URL: Final = SIRI_URL + "2.0/Siri_XML-v2.0.zip"

NETEX_ROOT: Final = "xsd/NeTEx_siri.xsd"
NETEX110_URL: Final = NETEX_URL + "1.10/NeTExXmlSchemaOnly-v1.10_2020.07.29.zip"
