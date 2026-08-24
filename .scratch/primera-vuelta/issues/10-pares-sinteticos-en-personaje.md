# 10 — Generación de los pares sintéticos en personaje

**What to build:** El material de entrenamiento del Adaptador: un lote de pares de diálogo
en personaje, en formato de chat, generados a partir del Corpus. Es un lote único offline
—puede tardar una noche— así que lo genera el modelo más grande que quepa en memoria, no
el pequeño que luego se va a afinar.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] Los pares se generan a partir de Pasajes reales del Corpus, no de conocimiento general del modelo generador
- [ ] El generador es el modelo más grande que quepa en la memoria disponible, distinto del Modelo Base que se va a afinar
- [ ] Los pares están en formato de chat, no en prosa de continuación
- [ ] Hay pares de los dos Universos y no se mezclan entre sí
- [ ] Queda anotado qué modelo generó el lote y con qué configuración, para poder rehacerlo
- [ ] Una muestra se revisa a mano antes de dar el lote por bueno
- [ ] El generador previsto es `google/gemma-4-31B-it`, de familia distinta al Modelo Base `Qwen/Qwen3-8B`
- [ ] **Si la segunda vuelta pasa a usar `gemma-4-31B-it` como Modelo Base**, este lote deja de ser válido: lo habría generado su propia familia y vuelve la auto-imitación. Regenerar con otra familia o dejar constancia de que se acepta
