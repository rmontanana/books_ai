# 11 — Entrenamiento del Adaptador

**What to build:** Un Adaptador entrenado sobre el Modelo Base con los pares sintéticos, y
convertido al formato que consume el stack de servicio. El artefacto que sale de aquí es lo
que el 12 conmuta en caliente.

**Blocked by:** 09, 10.

**Status:** ready-for-agent

- [ ] El entrenamiento produce un Adaptador, no un modelo completo modificado
- [ ] El Modelo Base queda intacto y verificablemente idéntico al de partida
- [ ] El Adaptador se convierte al formato que consume el stack de servicio
- [ ] La configuración del experimento queda registrada de forma que el entrenamiento se pueda repetir
- [ ] El tamaño del Adaptador es de cientos de MB, no del orden del modelo completo
