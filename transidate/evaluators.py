from typing import Iterable

from lxml import etree

from transidate.console import console
from transidate.datasets import DataSet
from transidate.results import Evaluation, EvaluationResult, Status


class XPathEvaluator:
    def __init__(self, expression: str, namespace: str):
        self.expression = expression
        self.namespace: str = namespace

    def evaluate(self, dataset: DataSet):
        evaluations = []
        for doc in dataset.documents():
            console.print(f"Evaluating {doc.name}.")
            root = doc.tree.getroot()
            ns = str(root.nsmap.get(None))
            namespaces = {self.namespace: ns}
            try:
                results = root.xpath(self.expression, namespaces=namespaces)
            except etree.XPathEvalError:
                return EvaluationResult(status=Status.error, items=[])

            if not isinstance(results, Iterable):
                results = [str(results)]

            for item in results:
                if isinstance(item, etree._Element):
                    evaluation = Evaluation.from_element(item)
                else:
                    evaluation = Evaluation(filename=doc.name, line=0, message=item)
                evaluations.append(evaluation)

        return EvaluationResult(status=Status.ok, items=evaluations)
