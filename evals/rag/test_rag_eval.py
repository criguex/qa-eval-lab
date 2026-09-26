"""
Modulo 2 — evaluacion de RAG.
Separa la calidad de la GENERACION (faithfulness, answer relevancy) de la del
RETRIEVAL (contextual relevancy) usando el retrieval_context de cada caso.

El caso 'international-wires' trae una respuesta que CONTRADICE el contexto
recuperado (alucinacion) → FaithfulnessMetric debe reprobarlo.

Correr:  deepeval test run evals/rag/test_rag_eval.py   (requiere OPENAI_API_KEY)
"""
import json
import os
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
)

HERE = os.path.dirname(__file__)

def load_cases():
    with open(os.path.join(HERE, "rag_dataset.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

faithfulness = FaithfulnessMetric(threshold=0.7)
answer_relevancy = AnswerRelevancyMetric(threshold=0.7)
context_relevancy = ContextualRelevancyMetric(threshold=0.6)

@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["input"][:30])
def test_rag_answer(case):
    tc = LLMTestCase(
        input=case["input"],
        actual_output=case["actual_output"],
        expected_output=case["expected_output"],
        retrieval_context=case["retrieval_context"],
    )
    assert_test(tc, [faithfulness, answer_relevancy, context_relevancy])
