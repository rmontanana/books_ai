# 03 — Corpus completo y limpieza del paratexto

**What to build:** Las 12 Obras del Corpus indexadas y consultables, con citas limpias.
Escalar de una Obra a doce es lo que obliga a limpiar: los pies editoriales aparecen en
casi todas las páginas de los libros de Martin y en tres de las de Tolkien, y hay
paratexto que responde consultas desde fuera de la ficción.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] Las 12 Obras del Corpus quedan indexadas; las dos excluidas siguen anotadas en el manifiesto y fuera del índice
- [ ] *El Señor de los Anillos* se trata como **una** Obra repartida en sus **cuatro** Volúmenes —los tres tomos y los *Apéndices*—, no como varias Obras
- [ ] El manifiesto declara a mano la correspondencia fichero → Volumen → Obra: el cuarto fichero se llama «El señor de los anillos 4 - Apendices», en minúsculas y sin tilde, y agrupar por prefijo lo deja fuera en silencio
- [ ] Los pies de `www.lectulandia.com` y `www.ArchivoTolkien.org` no aparecen en ningún Pasaje
- [ ] La presentación del editor de *Juego de tronos* y el epílogo del autor de *Danza de dragones* quedan fuera del índice
- [ ] **La limpieza no altera el mapa de páginas**: se limpia dentro de cada página, nunca entre páginas
- [ ] Existe una comprobación automática de que el número de páginas por **Volumen** es idéntico antes y después de limpiar
- [ ] Cada **Volumen** lleva registrado su Tipo de Texto: los tres tomos de *El Señor de los Anillos* son narrativa canónica y sus *Apéndices*, material de referencia, sin dejar de ser la misma Obra
- [ ] Una consulta cuya respuesta esté en una crónica interna lo refleja en la respuesta en vez de presentarlo como hecho establecido
- [ ] Toda Cita nombra un Volumen, nunca una Obra

## Comments

### La cuenta de Obras, corregida — 2026-08-24

El ticket decía «las **15 Obras** del Corpus». Son **12**: la etapa `inventario` del ticket
01 cuenta 15 ficheros en disco, y *El Señor de los Anillos* es una sola Obra repartida en
cuatro de ellos. El desglose medido, ya sin los dos ficheros excluidos:

| Universo | Ficheros | Obras | Páginas |
| --- | ---: | ---: | ---: |
| Martin | 8 | 8 | 5.695 |
| Tolkien | 7 | 4 | 1.917 |
| **Corpus** | **15** | **12** | **7.612** |

Las 7.612 páginas coinciden con las que decía `app.md`; lo que estaba mal era sólo la
cuenta de Obras.

### El Tipo de Texto de los *Apéndices*, resuelto — 2026-08-24

La casilla decía entonces «Cada Obra lleva registrado su Tipo de Obra» —el término se llama
ahora **Tipo de Texto**, por lo que se explica abajo— y chocaba con la de *El Señor de los
Anillos*: `app.md` llamaba a los *Apéndices* «material de referencia» —un Tipo propio— y a
la vez el cuarto fichero de una Obra cuyos otros tres son narrativa canónica. Una Obra lleva
**un** Tipo de Texto, así que las dos cosas no podían ser ciertas.

Lo resuelve el
[ADR-0006](../../../docs/adr/0006-la-cita-nombra-un-volumen-no-una-obra.md): el Tipo de Texto
—que hasta entonces se llamaba «Tipo de Obra», un nombre que señalaba al dueño equivocado—
cuelga del **Volumen**, no de la Obra. Los tres tomos son narrativa canónica, los
*Apéndices* material de referencia, y los cuatro siguen siendo *El Señor de los Anillos*. La
cuenta se queda en **12 Obras / 15 Volúmenes**.

El ADR sale de la Cita, no del Tipo: los cuatro ficheros numeran sus páginas desde 1, así
que «*El Señor de los Anillos*, p. 263» señala a tres a la vez. El Conjunto de Evaluación ya
lo había resuelto por su cuenta —cita «El Señor de los Anillos I/II/III» y «El Señor de los
Anillos: Apéndices» con páginas que caben en cada fichero—, y está congelado.

Sigue abierto **si los *Apéndices* se indexan**, que es otra pregunta: el 81% de sus páginas
están dentro de *El retorno del rey*, pero X02 los cita. Espera un dato de la extracción del
ticket 02. Si acaban fuera, el Corpus baja a 14 Volúmenes y 7.423 páginas, pero **las Obras
siguen siendo 12**.
