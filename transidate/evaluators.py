from typing import Iterable

from lxml import etree

from transidate.console import console
from transidate.datasets import DataSet
from transidate.results import Evaluation, EvaluationResult, Status


class XPathEvaluator:
    def __init__(self, expression: str, namespace: str):
        self.expression = expression
        self.namespace: str = namespace

    def wants_text(self):
        return self.expression.endswith("/text()")

    def get_context(self):
        if self.wants_text():
            *rest, last = self.expression.split("/")
            return "/".join(rest)
        return self.expression

    def evaluate(self, dataset: DataSet):
        evaluations = []

        for doc in dataset.documents():
            console.print(f"Evaluating {doc.name}.")
            root = doc.tree.getroot()
            ns = str(root.nsmap.get(None))
            namespaces = {self.namespace: ns}
            context = self.get_context()

            try:
                elements = root.xpath(context, namespaces=namespaces)
            except etree.XPathEvalError:
                return EvaluationResult(status=Status.error, items=[])

            breakpoint()

            evaluations = []
            if isinstance(elements, (float, bool, str, int)):
                message = f"{context} = {elements}"
                evaluations.append(
                    Evaluation(filename=doc.name, line=0, message=message)
                )
            elif not isinstance(elements, Iterable):
                evaluations.append(
                    Evaluation(filename=doc.name, line=0, message=elements)
                )
            else:
                for element in elements:
                    evaluation = Evaluation.from_element(element)
                    evaluations.append(evaluation)

        return EvaluationResult(status=Status.ok, items=evaluations)
