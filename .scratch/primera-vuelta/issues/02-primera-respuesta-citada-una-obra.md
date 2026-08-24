# 02 — Primera respuesta citada sobre una sola Obra

**What to build:** Preguntar por línea de comandos algo sobre *El Hobbit* y recibir una
respuesta con su Pasaje literal, el Volumen y la página. Es la bala trazadora: recorre
extracción, troceado, indexado, recuperación y generación, pero sobre una sola Obra
pequeña y limpia para que el circuito completo quepa de una vez.

**Blocked by:** 01.

**Status:** ready-for-agent

- [ ] *El Hobbit* queda extraído con su mapa de páginas —que pertenece al Volumen, no a la Obra— y troceado en Fragmentos de ~450 palabras con ~15% de solape
- [ ] Ningún Fragmento cruza el límite de un Volumen; si lo cruzara, su Cita no podría nombrar una sola página
- [ ] Cada Fragmento lleva antepuesta su cabecera de Obra y Universo antes de vectorizarse
- [ ] El índice es un único fichero SQLite, sin ningún proceso que levantar para consultarlo
- [ ] La recuperación es híbrida: vector denso más BM25 léxico
- [ ] La respuesta incluye Pasaje literal, **Volumen** y página, con la página anclada al comienzo del Pasaje y no a la del Fragmento
- [ ] **T03** («¿Cuántos enanos acompañan a Bilbo?») se responde «Trece» citando *El Hobbit*, p. 8
- [ ] **T04** (Smaug) se responde citando *El Hobbit*, p. 15
- [ ] Se comprueba a mano que la página citada contiene de verdad el Pasaje en el PDF original

## Comments

### La Cita nombra un Volumen — 2026-08-24

Este ticket se escribió antes del
[ADR-0006](../../../docs/adr/0006-la-cita-nombra-un-volumen-no-una-obra.md), así que decía
«la Obra y la página». La Cita nombra el **Volumen**, porque cada uno numera sus páginas
desde 1 y «*El Señor de los Anillos*, p. 263» señalaría a tres sitios a la vez.

Aquí apenas se nota —*El Hobbit* es una Obra de un solo Volumen, y T03 y T04 lo citan igual
en los dos modelos—, pero el mapa de páginas y la Cita hay que colgarlos del Volumen desde
el principio: es el ticket 03, con *El Señor de los Anillos*, el que lo pone a prueba, y
llegar allí con la estructura ya puesta cuesta mucho menos que retorcerla después.

**Un encargo que sale de aquí.** La otra decisión pendiente de `app.md` —si los *Apéndices*
siguen en el Corpus— espera un dato que produce la extracción de este ticket: en qué página
de *El retorno del rey* cae el pasaje que **X02** cita como «Apéndices, p. 61». Con eso se
sabe si excluir los *Apéndices* deja a X02 sin su Cita o simplemente la reubica. No hace
falta resolverlo aquí; sí anotar el dato en cuanto la extracción lo dé.
