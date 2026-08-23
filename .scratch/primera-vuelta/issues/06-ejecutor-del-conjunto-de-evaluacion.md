# 06 — Ejecutor del Conjunto de Evaluación

**What to build:** Un comando que corre las 58 preguntas del Conjunto de Evaluación y saca
un marcador desglosado por familia y por Universo. Es la vara de medir: a partir de aquí,
cambiar cualquier cosa del sistema produce un número comparable en vez de una impresión.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] Un solo comando ejecuta las 58 preguntas y produce un marcador
- [ ] El marcador se desglosa por familia (directa, multi-salto, negativa, cruzada) y por Universo
- [ ] Las directas y las multi-salto se puntúan por acierto **y** por corrección de la Cita, por separado: acertar el hecho citando la página equivocada no es un acierto completo
- [ ] Las negativas y las cruzadas se puntúan por abstención correcta
- [ ] El resultado queda guardado como artefacto identificable por Modelo Base y configuración, de forma que dos ejecuciones se puedan comparar
- [ ] El Conjunto de Evaluación se lee tal cual del fichero validado; el ejecutor nunca lo modifica
