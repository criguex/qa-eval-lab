# qa-eval-lab — Playwright + LLM-eval starter

Repo **portafolio** que junta lo que hoy casi nadie combina: pruebas de **UI (Playwright/TS)** + **evaluación de LLMs (DeepEval + Promptfoo)** + un **eval-gate en CI** que bloquea el merge si baja la calidad del modelo. Es el proyecto guía de la ruta *QA Automation → AI-Evaluation Engineer* y tu credencial #1 para reclutadores.

> Idea central: **eval = testing con superficie nueva.** El "bug" más peligroso de una feature de IA es el **false green** — un test en verde que no debería estarlo (la respuesta tiene la forma correcta pero el contenido está mal). Este repo lo caza.

## Qué demuestra
- **Playwright** con el patrón de auth real: el login lo haces una vez, se guarda `storageState`, y los tests lo reutilizan (`tests/auth.setup.ts`).
- **DeepEval** (el "pytest de LLMs"): `evals/test_llm_eval.py` con GEval (correctness) + AnswerRelevancy, incluyendo un test que demuestra el **false green**.
- **Promptfoo**: `evals/promptfooconfig.yaml` compara modelos, aplica `llm-rubric` y trae **red-teaming** (prompt injection, PII, jailbreak).
- **eval-gate en CI**: `.github/workflows/eval-gate.yml` corre UI + evals; si el score baja del umbral, **falla el pipeline**.

## Cómo correr
```bash
# UI (Playwright)
npm install
npx playwright install chromium
npm run test:ui
# Login manual (el que tú haces) para apps reales:
MANUAL_LOGIN=1 npx playwright test --project=setup --headed

# Evals de LLM (necesitan OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
pip install -r evals/requirements.txt
npm run eval:deepeval
npm run eval:promptfoo
npx promptfoo@latest redteam run   # seguridad
```

## Cómo mapea a la ruta de estudio
| Fase de la ruta | Qué tocas aquí |
|---|---|
| F1 LLM-as-judge | `GEval` con rúbrica en `test_llm_eval.py` |
| F2 Tooling | DeepEval + Promptfoo |
| F3 Red-teaming | `promptfoo redteam` |
| F3 Eval-gates CI/CD | `.github/workflows/eval-gate.yml` |
| F4 Capstone/portafolio | este repo público en github.com/criguex |

## Siguientes pasos (tú, mientras aprendes)
1. Cambia el caso trivial (capital de Colombia) por un caso REAL tuyo (un chatbot/feature).
2. Agrega un dataset (`evals/dataset.jsonl`) y corre las métricas sobre él.
3. Calibra tu judge: etiqueta 20 casos a mano y mide el % de acuerdo con GEval.
4. Publícalo en GitHub + escribe 1 post del proceso. Eso = inbound.

_Sin rastro de empleadores/clientes: es material propio (marca GWAR)._

## Módulo 1 — eval de un caso realista (empieza aquí)
`evals/dataset.jsonl` + `evals/test_support_eval.py`: un asistente de soporte fintech evaluado con **LLM-as-judge** (GEval) + AnswerRelevancy sobre un dataset. Dos casos traen respuestas incorrectas a propósito (dispute-window, card-blocked) → el judge debe reprobarlas = el **false green** que atrapa el eval-gate.

```bash
export OPENAI_API_KEY=sk-...
pip install -r evals/requirements.txt
deepeval test run evals/test_support_eval.py
```
Siguiente paso tuyo: reemplaza `dataset.jsonl` con casos reales de un feature de IA/QA tuyo y calibra el judge (etiqueta 15-20 a mano, mide el % de acuerdo).
