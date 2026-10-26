[Read in English](README.md)

![qa-eval-lab: pruebas UI con Playwright y evaluación de LLM (DeepEval · Promptfoo) detrás de un eval-gate en CI](docs/assets/banner.svg)

<p>
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/LLM_eval-DeepEval-55DFBD?style=flat-square&labelColor=071B2B" alt="DeepEval"/>
  <img src="https://img.shields.io/badge/LLM_eval-Promptfoo-55DFBD?style=flat-square&labelColor=071B2B" alt="Promptfoo"/>
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions"/>
  <img src="https://img.shields.io/badge/Licencia-MIT-55DFBD?style=flat-square&labelColor=071B2B" alt="Licencia: MIT"/>
</p>

La mayoría de las suites de pruebas verifican software **determinista**. Las funciones con IA son distintas: una respuesta puede venir bien formada y aun así estar **mal**, un **"falso verde"** que una aserción tipo `status == 200` o "el campo existe" deja pasar. `qa-eval-lab` pone las pruebas UI con Playwright y la evaluación de LLM (DeepEval + Promptfoo) detrás de un mismo **eval-gate** en CI, para que un cambio de modelo o de prompt que empiece a inventar haga fallar el pipeline antes de llegarle a un usuario.

> Proyecto de referencia para el paso **QA Automation → AI-Evaluation Engineer**: la disciplina de QA de siempre (cobertura, gates de regresión, pensar en modos de falla) aplicada a sistemas LLM no deterministas.

## Cómo funciona

![Cómo decide el eval-gate: un push corre un job de Playwright y un job de evaluación LLM (DeepEval y luego Promptfoo); si algún paso sale con código distinto de cero, el check falla](docs/assets/how-it-works.svg)

`.github/workflows/eval-gate.yml` corre dos jobs en cada push y pull request:

- **ui-tests**: `auth.setup.ts` inicia sesión una vez y guarda la sesión en `.auth/user.json` (`storageState`); las pruebas de `tests/ui/` la reutilizan.
- **llm-evals**: `deepeval test run test_llm_eval.py` califica las respuestas con `GEval` (LLM-as-judge) y `AnswerRelevancy`, ambos con umbral `0.7`; después `promptfoo eval` revisa `contains`, `not-contains` y `llm-rubric` contra `openai:gpt-4o-mini`.

Cualquier paso que salga con código distinto de cero pone el check en rojo. Si DeepEval falla, el job se detiene ahí y el paso de Promptfoo no corre.

![Animación: push, corren los dos jobs, la respuesta Bogota pasa, la respuesta Medellin falla en GEval, DeepEval sale con error, Promptfoo se salta y el check eval-gate queda en rojo](docs/assets/how-it-works.gif)

La animación usa los dos casos de `evals/test_llm_eval.py`. Los veredictos son los que esos casos deben obtener por diseño; no corrí el juez para hacerla porque necesita `OPENAI_API_KEY`.

## El "falso verde" en acción

`evals/dataset.jsonl` alimenta `evals/test_support_eval.py` (un asistente de soporte fintech). **Dos filas traen respuestas bien formadas pero falsas** a propósito:

| Caso | Pregunta | Respuesta incorrecta bajo prueba | Por qué el juez debe reprobarla |
|---|---|---|---|
| `dispute-window` | ¿Disputar un cobro de hace 90 días? | "Sí, cualquier cobro, sin límite de tiempo." | Ignora la ventana de ~60 días. |
| `card-blocked` | Tarjeta bloqueada tras 3 PIN errados | "Cancelada para siempre, no se recupera." | Se inventa un desenlace irreversible. |

Una aserción ingenua las deja pasar (*parecen* correctas). El **LLM-as-judge las reprueba**, y ese es el falso verde que el gate está hecho para atrapar.

![Animación: el caso dispute-window pasa dos aserciones ingenuas pero falla GEval Correctness con umbral 0.7; 2 de los 5 casos del dataset fallan y deepeval test run sale con error](docs/assets/gate-blocks.gif)

El texto del caso y el umbral son los reales del repo; los veredictos son los de diseño (este README y el docstring de la prueba), no una corrida grabada del juez.

## Cómo correrlo

**Requisitos:** Node 18+, Python 3.10+ y una `OPENAI_API_KEY` (u otro proveedor) para el LLM-as-judge.

```bash
# 1) Clonar
git clone https://github.com/criguex/qa-eval-lab.git && cd qa-eval-lab

# 2) Pruebas UI (Playwright)
npm install
npx playwright install chromium
npm run test:ui
#   apps reales: haz tú el login una vez y la sesión queda guardada
MANUAL_LOGIN=1 npx playwright test --project=setup --headed

# 3) Evaluación LLM (necesita OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
pip install -r evals/requirements.txt
deepeval test run evals/test_support_eval.py     # dataset realista (Módulo 1)
npm run eval:promptfoo                            # comparar modelos + rúbrica
npx promptfoo@latest redteam run                  # seguridad / red-team

# 4) Calibración del juez (sin conexión)
python evals/calibration/calibrate_judge.py
```

## Qué hay adentro

| Capa | Herramienta | Qué hace |
|---|---|---|
| **UI / E2E** | Playwright + TypeScript | Flujos contra `https://the-internet.herokuapp.com` (o `BASE_URL`) con el **patrón de autenticación** real (`storageState`): iniciar sesión una vez y reutilizarla en cada prueba. |
| **Evaluación de modelos** | DeepEval (estilo pytest) | `GEval` (LLM-as-judge), `AnswerRelevancy`, fidelidad al contexto y llamadas a herramientas sobre datasets. |
| **Prompts / seguridad** | Promptfoo | Comparación de modelos, aserciones `llm-rubric` y **red-teaming** (plugins `pii`, `harmful:misinformation`; estrategias `prompt-injection`, `jailbreak`). |
| **Gate** | GitHub Actions | Corre UI + evaluaciones en cada push/PR y **falla cuando un puntaje queda por debajo de su umbral**. |

### Cómo se decide cada veredicto

| Métrica | Pregunta que responde | Umbral |
|---|---|---|
| `GEval` (Correctness) | ¿La respuesta es correcta frente a la esperada? | `0.7` |
| `AnswerRelevancy` | ¿La respuesta sí atiende la pregunta? | `0.7` |
| `Faithfulness` (RAG) | ¿La respuesta se ciñe al contexto recuperado? | `0.7` |
| `ContextualRelevancy` (RAG) | ¿El contexto recuperado era pertinente? | `0.6` |
| `ToolCorrectness` (agente) | ¿El agente llamó las herramientas esperadas? | el de DeepEval (`0.5` en 4.3.1) |
| Promptfoo `llm-rubric` | ¿La salida cumple una rúbrica escrita? | según rúbrica |
| Promptfoo `redteam` | ¿Resiste inyección / PII / jailbreak? | según ataques |

Determinista donde la especificación lo permite; calificado contra criterios de aceptación donde no.

### Módulos

Cada módulo aísla un modo de falla que una revisión ingenua de "devolvió algo" no vería.

| # | Foco | Qué atrapa | Cómo correrlo |
|---|---|---|---|
| **1** | Respuestas de soporte | Respuestas bien formadas pero falsas (falsos verdes) | `deepeval test run evals/test_support_eval.py` |
| **2** | RAG | Alucinaciones que contradicen el contexto recuperado (el caso de giros internacionales); recuperación débil | `deepeval test run evals/rag/test_rag_eval.py` |
| **3** | Agentes | Respuesta final correcta por la *trayectoria equivocada* (p. ej. transfiere dinero **sin** revisar el saldo) | `deepeval test run evals/agent/test_agent_eval.py` |
| **4** | Calibración del juez | Un juez que nadie validó: mide el acuerdo humano↔juez + **κ de Cohen** y señala los desacuerdos | `python evals/calibration/calibrate_judge.py` |

Los módulos 1 y 2 necesitan `OPENAI_API_KEY` (LLM-as-judge). El módulo 4 corre sin conexión. El módulo 3 no hace llamadas a la API, pero DeepEval 4.3.1 no construye la métrica si `OPENAI_API_KEY` no está definida (sirve cualquier valor).

## Resultados reales

![Corrida real en terminal, 26 de octubre de 2026: Playwright 2 pasan y 1 falla; calibración del juez 8/10 de acuerdo y kappa de Cohen 0.58](docs/assets/local-run.gif)

Lo que corrí en mi máquina el 26 de octubre de 2026, sin clave de API:

- **Playwright** (`npx playwright test`, Playwright 1.64.1): `2 passed, 1 failed`. La prueba que falla (`sesion autenticada reutilizada`) espera el mensaje flash que sale una sola vez en `/secure`; la captura de la página muestra el Secure Area, o sea que la sesión sí se reutiliza, y la prueba de logout pasa.
- **Calibración del juez** (Módulo 4): 10 casos etiquetados, acuerdo `8/10 (80.0%)`, κ de Cohen `0.58`, por debajo del `0.6` que el propio script marca como "recalibrar rúbrica". Desacuerdos: `intl-wire` (humano fail, juez pass) y `refund-policy` (humano pass, juez fail).
- **Llamadas a herramientas del agente** (Módulo 3, DeepEval 4.3.1, clave de relleno): `happy-path-transfer` saca `1.0`; `skips-balance-check` saca `0.67` contra el umbral por defecto `0.5`, así que **pasa**. El caso que se quería atrapar no se atrapa hasta subir el umbral.

**CI hoy:** las cinco corridas en `main` (26 de septiembre de 2026) están en rojo. `llm-evals` se detiene al recolectar las pruebas porque el repo no tiene el secreto `OPENAI_API_KEY` (`DeepEvalError: OpenAI API key is empty`); `ui-tests` terminó con `1 passed, 2 failed` en la última corrida.

## Límites

- El paso de CI corre `test_llm_eval.py`, cuyo `test_false_green_detectado` evalúa con `assert_test` la respuesta falsa "Medellin". Con un juez funcionando esa prueba falla a propósito y el gate queda en rojo: es la demostración del gate bloqueando, no una suite pensada para quedar en verde.
- Los módulos 1 a 4 y `promptfoo redteam` se corren a mano; el workflow solo corre `test_llm_eval.py` y `promptfooconfig.yaml`.
- Un check en rojo solo bloquea el merge si `eval-gate` es un check obligatorio; `main` todavía no tiene protección de rama.
- Las pruebas UI apuntan a un sitio demo público (`the-internet.herokuapp.com`), así que su comportamiento puede cambiar sin aviso.
- Con Node 26, `npm install` falla compilando `better-sqlite3` (dependencia de Promptfoo); CI usa Node 20. Para la parte de Playwright basta `npm install --ignore-scripts`.

## Estructura del proyecto

```
qa-eval-lab/
├─ tests/
│  ├─ auth.setup.ts        # login una vez → storageState (el login lo haces tú)
│  └─ ui/example.spec.ts   # E2E reutilizando la sesión autenticada
├─ evals/
│  ├─ dataset.jsonl        # casos realistas de soporte fintech (2 son falsos verdes)
│  ├─ test_support_eval.py # Módulo 1 — LLM-as-judge sobre el dataset
│  ├─ test_llm_eval.py     # ejemplo mínimo de GEval + relevancia (corre en CI)
│  ├─ promptfooconfig.yaml # comparar modelos + rúbrica + red-team
│  ├─ rag/                 # Módulo 2 — RAG: fidelidad + relevancia del contexto
│  ├─ agent/               # Módulo 3 — trayectoria del agente: uso correcto de herramientas
│  ├─ calibration/         # Módulo 4 — acuerdo humano ↔ juez (kappa de Cohen)
│  └─ requirements.txt
├─ docs/
│  ├─ assets/              # banner, diagrama, animaciones GIF/MP4
│  └─ scenes/              # escenas HTML + export.mjs que genera las animaciones
├─ .github/workflows/
│  └─ eval-gate.yml        # UI + evaluaciones como gate en CI
├─ playwright.config.ts
└─ package.json
```

Las animaciones salen de `docs/scenes/*.html` con `node docs/scenes/export.mjs` (Playwright + ffmpeg); la versión MP4 de cada GIF está al lado en `docs/assets/`.

## Habilidades que muestra

`Playwright` · `TypeScript` · `Python` · `LLM-as-judge` · `DeepEval` · `Promptfoo` · `evaluación de RAG y agentes` · `red-teaming (OWASP LLM Top 10)` · `quality gates en CI/CD` · `GitHub Actions`

## Hoja de ruta

- [x] **Módulo 1** — dataset realista + LLM-as-judge
- [x] **Módulo 2** — evaluación de RAG (fidelidad + relevancia del contexto)
- [x] **Módulo 3** — evaluación de agentes / trayectoria (uso correcto de herramientas)
- [x] **Módulo 4** — reporte de calibración del juez (acuerdo humano ↔ juez, κ de Cohen)
- [ ] Capa de observabilidad (Arize Phoenix / Braintrust)

## Autor

**Cristian Guerra** — Senior SDET · QA Automation · AI-Evaluation, desde Medellín, Colombia (horarios de EE. UU.).

[GitHub](https://github.com/criguex) · [LinkedIn](https://www.linkedin.com/in/criguex) · disponible para contratos remotos en automatización de QA, SDET y evaluación de IA.

## Licencia

MIT © Cristian Guerra — ver [LICENSE](LICENSE).
