# 01 — Esqueleto de etapas y entorno reproducible

**What to build:** Un proyecto en el que se puede lanzar una etapa del pipeline, verla
producir su artefacto, volver a lanzarla y comprobar que reusa la caché en vez de rehacer
el trabajo. Y un servicio de embeddings que devuelve un vector real para una frase en
castellano. A partir de aquí, cualquier etapa posterior sólo tiene que declarar qué
consume y qué produce.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] El entorno corre sobre Python 3.12 gestionado con `uv`; el 3.14 del sistema no se usa
- [ ] Una etapa declara sus artefactos de entrada y salida, y se relanza por separado
- [ ] Relanzar una etapa sin cambios en su entrada no rehace el trabajo
- [ ] Invalidar la entrada de una etapa fuerza su recálculo y el de las que dependen de ella
- [ ] `llama-server` sirve un Modelo de Embeddings y devuelve un vector para una frase en castellano
- [ ] **Queda confirmado si BGE-M3 en GGUF carga en la build actual**; si no, se elige aquí el Modelo de Embeddings alternativo y se anota el motivo
- [ ] El Modo Consulta no depende de PyTorch en ningún punto
