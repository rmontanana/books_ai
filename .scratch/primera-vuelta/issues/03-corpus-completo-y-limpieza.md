# 03 — Corpus completo y limpieza del paratexto

**What to build:** Las 12 Obras del Corpus indexadas y consultables, con citas limpias.
Escalar de una Obra a doce es lo que obliga a limpiar: los pies editoriales aparecen en
casi todas las páginas de los libros de Martin y en tres de las de Tolkien, y hay
paratexto que responde consultas desde fuera de la ficción.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] Las 12 Obras del Corpus quedan indexadas; las dos excluidas siguen anotadas en el manifiesto y fuera del índice
- [ ] *El Señor de los Anillos* se trata como **una** Obra repartida en sus **cuatro** ficheros —los tres tomos y los *Apéndices*—, no como varias Obras
- [ ] El manifiesto declara a mano qué fichero es de qué Obra: el cuarto se llama «El señor de los anillos 4 - Apendices», en minúsculas y sin tilde, y agrupar por prefijo lo deja fuera en silencio
- [ ] Los pies de `www.lectulandia.com` y `www.ArchivoTolkien.org` no aparecen en ningún Pasaje
- [ ] La presentación del editor de *Juego de tronos* y el epílogo del autor de *Danza de dragones* quedan fuera del índice
- [ ] **La limpieza no altera el mapa de páginas**: se limpia dentro de cada página, nunca entre páginas
- [ ] Existe una comprobación automática de que el número de páginas por Obra es idéntico antes y después de limpiar
- [ ] Cada Obra lleva registrado su Tipo de Obra
- [ ] Una consulta cuya respuesta esté en una crónica interna lo refleja en la respuesta en vez de presentarlo como hecho establecido

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

**Un cabo suelto que es de este ticket.** La casilla «Cada Obra lleva registrado su Tipo de
Obra» choca con la de *El Señor de los Anillos*: `app.md` llama a los *Apéndices* «material
de referencia» —un Tipo de Obra propio— y a la vez los cuenta como el cuarto fichero de una
Obra cuyos otros tres son narrativa canónica. Una Obra lleva **un** Tipo de Obra, así que
hay que elegir: o los *Apéndices* salen como Obra aparte y el Corpus tiene **13**, o
heredan el Tipo de *El Señor de los Anillos* y se quedan en 12. Las cifras de arriba
suponen lo segundo, que es lo que dice `app.md` en la frase de los cuatro ficheros.

Es la misma decisión que la de si los *Apéndices* siguen en el Corpus (el 81% de sus
páginas están dentro de *El retorno del rey*), y sigue abierta en el «Pendiente de decidir»
de `app.md`. Si acaban fuera, el Corpus baja a 14 ficheros y 7.423 páginas, pero **las
Obras siguen siendo 12**.
