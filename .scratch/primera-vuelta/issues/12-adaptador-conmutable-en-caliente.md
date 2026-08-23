# 12 — Adaptador conmutable en caliente

**What to build:** El Modo Personaje responde con voz de verdad, y el Modo Consulta sigue
corriendo sobre el Modelo Base sin tocar. Cambiar de Modo activa o desactiva el Adaptador
sin recargar el modelo ni reiniciar el servicio.

**Blocked by:** 08, 11.

**Status:** ready-for-agent

- [ ] Activar y desactivar el Adaptador no obliga a reiniciar el servicio ni a recargar los pesos del Modelo Base
- [ ] Modo Consulta corre siempre sobre el Modelo Base sin Adaptador
- [ ] El marcador del Conjunto de Evaluación no empeora respecto al del ticket 06: **ningún entrenamiento puede degradar la herramienta**
- [ ] Los prompts fijos de Modo Personaje se releen y se compara la voz con la del ticket 08
- [ ] Tener varios Adaptadores disponibles no multiplica la memoria ocupada por el modelo
