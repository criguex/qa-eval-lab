"""
Modulo 1 — eval de un caso realista: asistente de soporte fintech.
Lee evals/dataset.jsonl y evalua cada respuesta con LLM-as-judge (GEval) + AnswerRelevancy.

Dos casos del dataset tienen actual_output INCORRECTO a proposito (dispute-window, card-blocked):
un assert ingenuo los dejaria pasar (tienen la forma correcta) y el judge debe REPROBARLOS.
Ese es el "false green" que atrapa el eval-gate.

Correr:  deepeval test run test_support_eval.py     (requiere OPENAI_API_KEY)
Cambia dataset.jsonl por tus propios casos reales cuando quieras.
"""
import json
import os
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric

HERE = os.path.dirname(__file__)

def load_cases():
    with open(os.path.join(HERE, "dataset.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

correctness = GEval(
    name="Correctness",
    criteria=(
        "Decide si 'actual_output' es factualmente correcto y consistente con 'expected_output' "
        "para el 'input'. Reprueba fuerte cualquier afirmacion inventada, contradictoria o "
        "que exagere/omita limites (plazos, montos, condiciones)."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    threshold=0.7,
)

relevancy = AnswerRelevancyMetric(threshold=0.7)

@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["id"])
def test_support_answer(case):
    tc = LLMTestCase(
        input=case["input"],
        actual_output=case["actual_output"],
        expected_output=case["expected_output"],
    )
    assert_test(tc, [correctness, relevancy])
