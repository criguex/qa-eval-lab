"""
Modulo 3 — evaluacion de agentes (trajectory / tool-use).
No basta con la respuesta final: un agente debe llamar las herramientas correctas,
en el orden correcto. ToolCorrectnessMetric compara tools_called vs expected_tools
(es determinista, no necesita LLM).

Caso 'skips-balance-check': el agente transfiere SIN verificar saldo → debe reprobar.

Correr:  deepeval test run evals/agent/test_agent_eval.py
"""
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric

tool_correctness = ToolCorrectnessMetric()

CASES = [
    {
        "id": "happy-path-transfer",
        "input": "Transfer $100 to John",
        "actual_output": "Sent $100 to John. New balance: $400.",
        "tools_called": [ToolCall(name="check_balance"), ToolCall(name="get_payee"), ToolCall(name="transfer_funds")],
        "expected_tools": [ToolCall(name="check_balance"), ToolCall(name="get_payee"), ToolCall(name="transfer_funds")],
    },
    {
        "id": "skips-balance-check",
        "input": "Transfer $100 to John",
        "actual_output": "Sent $100 to John.",
        "tools_called": [ToolCall(name="get_payee"), ToolCall(name="transfer_funds")],
        "expected_tools": [ToolCall(name="check_balance"), ToolCall(name="get_payee"), ToolCall(name="transfer_funds")],
    },
]

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_agent_tools(case):
    tc = LLMTestCase(
        input=case["input"],
        actual_output=case["actual_output"],
        tools_called=case["tools_called"],
        expected_tools=case["expected_tools"],
    )
    assert_test(tc, [tool_correctness])
