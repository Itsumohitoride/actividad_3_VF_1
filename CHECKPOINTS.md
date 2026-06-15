# CHECKPOINTS — Evaluacion del estado final

> En sistemas multi-agente no se evalua el camino, se evalua el destino.
> Estos son los checkpoints objetivos que un juez (humano o IA) puede usar
> para decidir si el proyecto esta sano.

## C1 — El arnes esta completo

- [ ] Existen los 4 archivos base: `AGENTS.md`, `scripts/check_harness.py`, `feature_list.json`,
      `progress/current.md`.
- [ ] Existen los 3 docs: `docs/architecture.md`, `docs/conventions.md`,
      `docs/verification.md`.
- [ ] `python3 scripts/check_harness.py` termina con exit code 0.

## C2 — El estado es coherente

- [ ] Como mucho una feature en `in_progress` en `feature_list.json`.
- [ ] Toda feature `done` tiene tests asociados que pasan.
- [ ] Toda feature con estado `testing` tiene al menos una transicion
      `from: "in_progress", to: "testing"`.
- [ ] El ultimo `to` del array `transitions` coincide con el `status` actual.
- [ ] `progress/current.md` esta vacio o describe la sesion activa
      (no contiene basura de sesiones anteriores).

## C3 — El codigo respeta la arquitectura

- [ ] El codigo en `src/` respeta la organizacion definida en `docs/architecture.md`.
- [ ] No hay dependencias externas no declaradas.
- [ ] No hay `print()`/`console.log()` sueltos para debug, ni TODOs sin contexto.
- [ ] Dockerfile sigue convenciones multi-stage, non-root, HEALTHCHECK.
- [ ] Helm charts siguen convenciones de naming y estructura.

## C4 — La verificacion es real

- [ ] El microservicio tiene tests unitarios.
- [ ] `docker build --no-cache` pasa sin errores.
- [ ] `helm lint` pasa sin errores.
- [ ] El comando de tests definido en `scripts/check_harness.py` muestra > 0 tests y todos verdes.

## C5 — La sesion se cerro bien

- [ ] No hay archivos sin trackear sospechosos (`*.tmp`, `__pycache__`,
      `node_modules/` no ignorados, etc.).
- [ ] `progress/history.md` tiene una entrada por la ultima sesion.
- [ ] La ultima feature trabajada esta reflejada en su estado correcto.

## C6 — Costo de sesion registrado

- [ ] `progress/cost_log.json` existe y tiene estructura valida.
- [ ] La ultima feature completada tiene una entrada de costo en
      `progress/cost_log.json`.
- [ ] Los campos de la entrada son completos y veraces (modelo, tokens,
      costo USD, duracion, agentes participantes).

## C7 — Documentacion de despliegue y configuracion

- [ ] `docs/deployment.md` existe y no es la plantilla vacia (tiene
      contenido relevante al proyecto).
- [ ] `docs/configuration.md` existe y no es la plantilla vacia (tiene
      contenido relevante al proyecto).
- [ ] Si la ultima feature afecto despliegue o configuracion,
      los documentos correspondientes se actualizaron.

---

**Como usar este archivo:** un agente revisor recorre cada checkbox,
marca `[x]` o `[ ]`, y rechaza el cierre de sesion si quedan boxes
vacios en C1-C7.
