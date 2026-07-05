# fable-forge

Generador de fábulas interactivas. El usuario da una **moraleja/tema**, una
**audiencia** (ej. edad) y un **tono**, y el módulo genera una fábula original
con personajes-animal, conflicto y moraleja explícita. Soporta variantes de
formato y series con personajes recurrentes.

**Backend único: `claude-fable-5` vía Messages API.** Sin RAG, sin base de
datos, sin dependencias de otros servicios ni de otros módulos del repo. La
persistencia (fábulas y series) son archivos planos en `output/`.

## Setup

```sh
cd fable-forge
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # o un perfil de `ant auth login`
```

## Uso

```sh
# Fábula nueva
python -m fable_forge new -m "no hay que mentir" -a "6-8 años" -t "humor tierno"

# Con serie (personajes recurrentes): la primera llamada crea la serie,
# las siguientes reutilizan personajes, escenario y evitan repetir moralejas
python -m fable_forge new -m "pedir ayuda no es debilidad" -a "9-12" -t "aventura" --serie bosque-gris
python -m fable_forge new -m "la paciencia rinde" -a "9-12" -t "aventura" --serie bosque-gris

# Variantes de formato sobre una fábula ya generada
python -m fable_forge variant output/fables/<archivo>.md --tipo corta
python -m fable_forge variant output/fables/<archivo>.md --tipo verso
python -m fable_forge variant output/fables/<archivo>.md --tipo guion
python -m fable_forge variant output/fables/<archivo>.md --tipo ilustraciones

# Series
python -m fable_forge series list
python -m fable_forge series show bosque-gris
```

Las fábulas se imprimen por stdout y se guardan en `output/fables/`
(configurable con `FABLE_FORGE_DATA`).

## Diseño

```
fable_forge/
├── prompts.py   # system prompt y prompts de variantes — EL corazón del módulo
├── client.py    # llamada a la API (claude-fable-5, manejo de refusal/fallback)
├── storage.py   # fábulas .md + series .json en archivos planos
└── cli.py       # argparse
```

### El system prompt es el producto

La calidad del output vive en `prompts.py`, no en el código. Decisiones clave:

- **Reglas innegociables vs. calibrables.** Estructura (personajes-animal,
  arco, moraleja explícita) separada de lo que se adapta (edad, tono), para que
  el modelo sepa qué flexibilizar.
- **Moraleja ganada, no pegada.** La regla central: la historia demuestra la
  moraleja, la frase final solo la nombra. Prohibido el sermón a mitad del
  relato.
- **Originalidad explícita.** Sin recuentos de Esopo/La Fontaine ni parejas
  icónicas gastadas (tortuga/liebre, cigarra/hormiga); el modo de falla más
  común de un LLM pidiendo "una fábula".
- **Bloque `fable-meta`.** Cada fábula termina con un JSON parseable
  (personajes, escenario, resumen). Es lo que hace posible las series sin base
  de datos: el CLI acumula esa metadata en un JSON por serie y la reinyecta
  como bloque `<serie>` en la generación siguiente.
- **Variantes con system prompt propio.** Las variantes (corta, verso, guion,
  ilustraciones) usan un prompt de "modo adaptación" que fija la invariante:
  transformar el formato sin tocar historia, personajes ni moraleja.

### Notas sobre claude-fable-5

- El thinking está siempre activo y no se configura (no se pasa `thinking`);
  tampoco acepta `temperature`. El presupuesto de thinking cuenta contra
  `max_tokens`, de ahí el default de 16000.
- El system prompt lleva `cache_control` (prompt caching): tandas de fábulas o
  variantes dentro de la ventana de caché reutilizan el prefijo.
- Los clasificadores de seguridad pueden declinar un pedido
  (`stop_reason: "refusal"`). Improbable para fábulas, pero está manejado: por
  defecto se opta al fallback server-side hacia `claude-opus-4-8` **solo** para
  ese caso. Si querés exclusividad estricta de `claude-fable-5`, seteá
  `FABLE_FORGE_NO_FALLBACK=1` (un pedido declinado entonces falla con código de
  salida 2).
