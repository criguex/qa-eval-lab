"""
Eval de LLM estilo pytest con DeepEval.
Demuestra el "false green": una salida con la FORMA correcta pero contenido MAL,
que un assert ingenuo (status 200 / campo existe) dejaria pasar y un judge NO.

Requiere OPENAI_API_KEY (o el provider que configures). Ver README.
Correr:  deepeval test run test_llm_eval.py
"""
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric

correctness = GEval(
    name="Correctness",
    criteria=(
        "Evalua si 'actual_output' es factualmente correcto y responde el 'input' "
        "de acuerdo con 'expected_output'. Penaliza fuerte alucinaciones o datos inventados."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    threshold=0.7,
)

relevancy = AnswerRelevancyMetric(threshold=0.7)


def test_respuesta_correcta():
    tc = LLMTestCase(
        input="Cual es la capital de Colombia?",
        actual_output="La capital de Colombia es Bogota.",
        expected_output="Bogota",
    )
    assert_test(tc, [correctness, relevancy])


def test_false_green_detectado():
    # Respuesta bien formada pero FALSA: el judge debe reprobarla.
    tc = LLMTestCase(
        input="Cual es la capital de Colombia?",
        actual_output="La capital de Colombia es Medellin.",
        expected_output="Bogota",
    )
    assert_test(tc, [correctness])
