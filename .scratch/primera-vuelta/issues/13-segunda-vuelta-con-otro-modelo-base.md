# 13 — Segunda vuelta con otro Modelo Base

**What to build:** Rehacer el circuito completo con un Modelo Base de clase 27–32B y poner
los dos marcadores uno al lado del otro. Es el cobro de todo lo anterior: la repetibilidad
del pipeline y la vara de medir sólo valen algo si se usan para decidir.

**Blocked by:** 06, 12.

**Status:** ready-for-agent

- [ ] Cambiar de Modelo Base es un cambio de configuración, no una reescritura
- [ ] Las etapas que no dependen del Modelo Base —extracción, limpieza, troceado, indexado— **no se rehacen**
- [ ] Se obtiene un segundo marcador comparable con el primero, con el mismo Conjunto de Evaluación sin modificar
- [ ] La comparación se hace por familia y por Universo, no con una sola cifra global
- [ ] Queda escrito qué Modelo Base gana, en qué familias, y si la diferencia justifica su coste
