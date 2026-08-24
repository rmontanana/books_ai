# 06 — Ejecutor del Conjunto de Evaluación

**What to build:** Un comando que corre las 58 preguntas del Conjunto de Evaluación y saca
un marcador desglosado por familia y por Universo. Es la vara de medir: a partir de aquí,
cambiar cualquier cosa del sistema produce un número comparable en vez de una impresión.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] Un solo comando ejecuta las 58 preguntas y produce un marcador
- [ ] El marcador se desglosa por familia (directa, multi-salto, negativa, cruzada) y por Universo
- [ ] Las directas y las multi-salto se puntúan por acierto **y** por corrección de la Cita, por separado: acertar el hecho citando la página equivocada no es un acierto completo
- [ ] La Cita se compara contra el **Volumen**, no contra la Obra: el campo `obra:` del YAML contiene un nombre de Volumen («El Señor de los Anillos III: El retorno del rey»)
- [ ] Las negativas y las cruzadas se puntúan por abstención correcta
- [ ] El resultado queda guardado como artefacto identificable por Modelo Base y configuración, de forma que dos ejecuciones se puedan comparar
- [ ] El Conjunto de Evaluación se lee tal cual del fichero validado; el ejecutor nunca lo modifica

## Comments

### El campo `obra:` del YAML contiene un Volumen — 2026-08-24

Trampa para quien escriba el ejecutor. El
[ADR-0006](../../../docs/adr/0006-la-cita-nombra-un-volumen-no-una-obra.md) separó la Obra
(el texto publicado, 12) del Volumen (lo que la Cita nombra y lo que numera sus páginas
desde 1, 15). El `eval/conjunto-evaluacion.yaml` es anterior y **está congelado**: su campo
se sigue llamando `obra`, pero lo que guarda es el nombre de un Volumen. Se ve en sus
propios valores —«El Señor de los Anillos I: La comunidad del anillo», «… III: El retorno
del rey», «El Señor de los Anillos: Apéndices»— y en que las páginas caben dentro de cada
fichero: la 263, la 309, la 406 y la 61.

No se renombra el campo. El Conjunto de Evaluación no cambia entre experimentos; si cambia,
deja de servir para comparar. El ejecutor traduce.
