---
name: skill-mesh-architect
description: Diseña, audita y optimiza Skills de Claude Code como nodos interconectados de un ecosistema agéntico. Genera archivos SKILL.md con frontmatter de enrutamiento determinista, aplica divulgación progresiva (cuerpo mínimo + references/ y scripts/ bajo demanda) y cablea delegación explícita entre skills globales (~/.claude/skills/) y de proyecto (.claude/skills/) sin duplicar lógica. Úsese cuando el usuario solicite crear, evaluar, refactorizar, empaquetar o interconectar una skill; auditar frontmatter, descripciones o consumo de tokens; encadenar habilidades o delegar a subagentes; o mencione SKILL.md, ecosistema de agentes, divulgación progresiva, enrutamiento de habilidades o modularización de contexto, incluso si no usa la palabra "skill" explícitamente.
---

# Skill Mesh Architect

## Propósito y Contexto

Operar como arquitecto de infraestructura cognitiva. Cada skill es un nodo con responsabilidad única dentro de una malla; el valor del sistema reside en las aristas (delegación explícita), no en nodos monolíticos. Todo artefacto emitido debe ser ejecutable a ciegas por un modelo secundario más veloz (Opus/Sonnet/Haiku) sin interpretación adicional ni preguntas de clarificación. La economía de tokens es una restricción de diseño de primer orden, no una optimización posterior.

## Reglas Inquebrantables

1. **Frontmatter como motor de enrutamiento.** `name` en kebab-case, ≤64 caracteres, sin mayúsculas, espacios ni guiones bajos. `description` <1024 caracteres: inicia declarando la capacidad y cierra con cláusula "Úsese cuando..." que enumere palabras clave disparadoras Y escenarios adyacentes donde el usuario no usa el término exacto (los modelos sub-disparan skills; la descripción debe ser insistente). Descripción vaga = nodo inexistente para el enrutador.
2. **Una skill, una responsabilidad.** Si el diseño exige "y además...", dividir en dos nodos y conectarlos por contrato de delegación.
3. **Divulgación progresiva en tres niveles.** Nivel 1: metadata (name+description, siempre en contexto). Nivel 2: cuerpo del SKILL.md, ≤500 líneas. Nivel 3: `references/*.md` (documentación bajo demanda; si un archivo supera 300 líneas, incluir tabla de contenidos), `scripts/` (código ejecutable sin cargar al contexto), `assets/` (plantillas para el output).
4. **Cero duplicación.** Si una capacidad existe en otro nodo del ecosistema, delegar con contrato explícito. Prohibido copiar su lógica inline.
5. **Voz imperativa activa.** Cada directriz indica la acción con comando, ruta o métrica verificable. Ninguna aspiración sin criterio de cumplimiento.
6. **Determinismo de salida.** Definir el árbol de archivos y el orden de secciones del entregable antes de redactar contenido.

## Conexión y Delegación Multi-Skill

**Descubrimiento (ejecutar al inicio de toda tarea de orquestación):**

```bash
for f in ~/.claude/skills/*/SKILL.md .claude/skills/*/SKILL.md; do
  [ -f "$f" ] && echo "── $f" && awk '/^---$/{n++; next} n==1' "$f"
done
```

Cargar únicamente frontmatters para decidir enrutamiento. Prohibido leer cuerpos completos en fase de descubrimiento. Precedencia: skill de proyecto (`.claude/skills/`) sobrescribe a la global homónima (`~/.claude/skills/`).

**Contrato de delegación (bloque mandatorio dentro de toda skill macro que consuma un nodo especializado):**

```
DELEGAR → <nombre-skill>
Ruta: ~/.claude/skills/<nombre-skill>/SKILL.md
Input: <datos exactos que se entregan>
Output esperado: <artefacto y formato de retorno>
Aislamiento: inline | subagente
```

Semántica de ejecución: leer la SKILL.md declarada, ejecutar su Procedimiento con el input entregado y retornar al flujo principal únicamente el output declarado, descartando el contexto intermedio del nodo. Con `Aislamiento: subagente`, lanzar la tarea vía Task tool incluyendo la ruta de la skill en el prompt del subagente.

**Modo de fallo:** si la ruta declarada no existe, detener la ejecución, reportar el nodo faltante con su ruta esperada y NO reimplementar la capacidad inline.

**Referencias internas:** enlazar material pesado con instrucción de carga condicionada: `Leer references/<archivo>.md solo al ejecutar el paso N`.

## Procedimiento de Ejecución

**Fase 1 — Ingesta y mapeo.** Leer el contexto del usuario. Ejecutar el comando de descubrimiento. Listar frontmatters existentes y detectar solapamientos de responsabilidad con la skill solicitada.

**Fase 2 — Diseño del nodo.** Definir: `name`, responsabilidad única, dependencias (nodos existentes a los que delegará) y partición de contenido (SKILL.md vs `references/` vs `scripts/` vs `assets/`).

**Fase 3 — Redacción.** Escribir primero el frontmatter y validarlo contra la Regla 1. Redactar el cuerpo en este orden fijo: Propósito y Contexto → Reglas Inquebrantables → Conexión y Delegación Multi-Skill → Procedimiento de Ejecución → Protocolo de Auto-Verificación.

**Fase 4 — Cableado.** Insertar un bloque `DELEGAR` por cada dependencia identificada en Fase 2, con ruta, input, output y modo de aislamiento exactos.

**Fase 5 — Empaquetado.** Emitir el árbol de archivos completo y el contenido de cada archivo. Si se optimiza una skill existente: preservar el `name` original, copiar a ubicación escribible antes de editar, y emitir la lista de cambios en formato `[líneas extraídas del cuerpo] → [destino: references/ | scripts/ | skill delegada]`.

## Protocolo de Auto-Verificación

Auditar contra esta lista antes de finalizar el turno. Cualquier ítem fallido obliga a corregir y re-verificar.

- [ ] `name`: kebab-case, ≤64 caracteres, sin mayúsculas/espacios/guiones bajos.
- [ ] `description`: <1024 caracteres, cierra con cláusula "Úsese cuando..." con palabras clave y escenarios adyacentes.
- [ ] Cuerpo ≤500 líneas (`wc -l SKILL.md`); material pesado movido a `references/`; referencias >300 líneas con tabla de contenidos.
- [ ] Cero lógica duplicada respecto a nodos descubiertos en Fase 1.
- [ ] Cada bloque `DELEGAR` contiene ruta + input + output + aislamiento.
- [ ] Toda directriz en voz imperativa con acción o métrica verificable.
- [ ] Un modelo secundario puede ejecutar el artefacto sin formular preguntas de clarificación.
