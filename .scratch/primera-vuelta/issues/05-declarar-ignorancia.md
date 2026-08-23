# 05 — Declarar ignorancia cuando el Corpus no cubre

**What to build:** Cuando la respuesta no está en el Corpus, el sistema lo dice en vez de
improvisar. Es el único fallo que de verdad importa en Modo Consulta: una respuesta
inventada con una Cita de aspecto correcto es peor que ninguna respuesta.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] Las nueve Preguntas Negativas **N01–N09** obtienen una declaración de ignorancia, no una respuesta
- [ ] Ninguna respuesta se emite sin al menos un Pasaje recuperado que la sostenga
- [ ] Un Pasaje recuperado que no sostiene la afirmación no basta: se prefiere callar
- [ ] **M14** (la madre de Jon Nieve) atribuye la afirmación a quien la dice y no la presenta como hecho establecido
