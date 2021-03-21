from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

from tests.constants import TXC_END, TXC_START
from transidate.datasets import DataSet
from transidate.evaluators import XPathEvaluator
from transidate.results import Status


class XMLFile(BytesIO):
    def __init__(self, xml: str, **kwargs):
        super().__init__(**kwargs)
        self.write(xml.encode("utf-8"))
        self.name = "txc.xml"
        self.seek(0)


class TXCFile(XMLFile):
    def __init__(self, txc: str, **kwargs):
        txc = TXC_START + txc + TXC_END
        super().__init__(txc, **kwargs)


def test_successful_aggregate_evaluation():
    xml = """
    <NptgLocalities>
        <AnnotatedNptgLocalityRef>
            <NptgLocalityRef>E0000004</NptgLocalityRef>
            <LocalityName>Hinckley</LocalityName>
        </AnnotatedNptgLocalityRef>
    </NptgLocalities>
    """
    xml_file = TXCFile(xml)
    path = Mock(spec=Path)
    path.open.return_value = xml_file
    dataset = DataSet(path)
    expression = "count(//x:LocalityName)"
    namespace = "x"
    evaluator = XPathEvaluator(expression, namespace)
    result = evaluator.evaluate(dataset)
    assert result.status == Status.ok
    assert result.item_count == 1
    assert result.items[0].message == "1.0"


def test_malformed_expression_evaluation():
    xml = """
    <NptgLocalities>
        <AnnotatedNptgLocalityRef>
            <NptgLocalityRef>E0000004</NptgLocalityRef>
            <LocalityName>Hinckley</LocalityName>
        </AnnotatedNptgLocalityRef>
    </NptgLocalities>
    """
    xml_file = TXCFile(xml)
    path = Mock(spec=Path)
    path.open.return_value = xml_file
    dataset = DataSet(path)
    expression = "count(//x:LocalityName"
    namespace = "x"
    evaluator = XPathEvaluator(expression, namespace)
    result = evaluator.evaluate(dataset)
    assert result.status == Status.error
    assert result.item_count == 0


def test_element_expression_evaluation():
    xml = """
    <NptgLocalities>
        <AnnotatedNptgLocalityRef>
            <NptgLocalityRef>E0000004</NptgLocalityRef>
            <LocalityName>Hinckley</LocalityName>
        </AnnotatedNptgLocalityRef>
        <AnnotatedNptgLocalityRef>
            <NptgLocalityRef>E0000005</NptgLocalityRef>
            <LocalityName>Grover</LocalityName>
        </AnnotatedNptgLocalityRef>
    </NptgLocalities>
    """
    xml_file = TXCFile(xml)
    path = Mock(spec=Path)
    path.open.return_value = xml_file
    dataset = DataSet(path)
    expression = "//x:LocalityName"
    ns = "http://www.transxchange.org.uk/"
    namespace = "x"
    evaluator = XPathEvaluator(expression, namespace)
    result = evaluator.evaluate(dataset)
    assert result.status == Status.ok
    assert result.item_count == 2
    assert result.items[0].message == f"{{{ns}}}LocalityName"
