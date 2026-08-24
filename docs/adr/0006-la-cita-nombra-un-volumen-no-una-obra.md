# La Cita nombra un Volumen, no una Obra

«Obra» estaba haciendo dos trabajos a la vez: decir qué texto publicado es algo —por lo que
*El Señor de los Anillos* es una y no cuatro— y ser lo que la Cita nombra, que además posee
el mapa de páginas. Mientras cada Obra llegó en un solo fichero los dos trabajos
coincidieron, y nadie notó que eran dos.

Con *El Señor de los Anillos* dejan de coincidir, y lo que sale no es una imprecisión: es
una Cita rota. Sus cuatro ficheros numeran las páginas desde 1 cada uno, así que «*El Señor
de los Anillos*, p. 263» señala a la vez a *La comunidad del anillo*, a *Las dos torres* y a
*El retorno del rey*. La Cita existe para verificar una respuesta sin abrir el PDF, y una
que apunta a tres sitios no verifica nada.

El Conjunto de Evaluación ya lo había resuelto por su cuenta antes de que existiera este
documento. Cita cuatro unidades distintas —«El Señor de los Anillos I: La comunidad del
anillo», «… II: Las dos torres», «… III: El retorno del rey» y «El Señor de los Anillos:
Apéndices»— con páginas que caben dentro de cada fichero: la 263 de la primera, la 309 de la
segunda, la 406 de la tercera, la 61 de los *Apéndices*. Esas cadenas son `Obra` + `Volumen`
aplanados en el único campo que había. Está validado y congelado, así que el modelo de datos
se ajusta a él y no al revés.

Se separan los dos trabajos en dos términos:

- La **Obra** sigue siendo el texto publicado. Son 12.
- El **Volumen** es lo que la Cita nombra y lo que posee el mapa de páginas. Son 15, uno por
  fichero. Para 11 de las 12 Obras la correspondencia es 1:1 y no cambia nada.

El **Tipo de Texto** pasa a colgar del Volumen. Eso cierra de paso una contradicción que
estaba escrita en el diseño: los *Apéndices* eran a la vez «material de referencia» —un Tipo
propio— y el cuarto fichero de una Obra cuyos otros tres son narrativa canónica. Una Obra
lleva **un** Tipo de Texto, así que las dos cosas no podían ser ciertas. Colgándolo del
Volumen, los tres tomos son narrativa canónica, los *Apéndices* material de referencia, y
los cuatro siguen siendo *El Señor de los Anillos*.

La alternativa era declarar 15 Obras y quitar el nivel de encima. Resuelve la contradicción
igual de bien y cuesta menos hoy, pero deja de poder decir que *El Señor de los Anillos* es
un solo texto, tira el ejemplo con el que `CONTEXT.md` define Obra, y tira el nivel que el
Conjunto de Evaluación ya estaba codificando a mano en cada una de sus cadenas.

## Consecuencias

- La **Cita es Volumen + página**, no Obra + página.
- El **manifiesto declara a mano** la correspondencia fichero → Volumen → Obra. No se deduce
  del nombre: el cuarto fichero de *El Señor de los Anillos* se llama «El señor de los
  anillos 4 - Apendices», en minúsculas y sin tilde, mientras los otros tres empiezan por
  «El Señor de los Anillos - 0N». Agruparlos por prefijo lo deja fuera sin avisar.
- Un **Fragmento no cruza el límite de un Volumen**. Si lo cruzara, su Cita no podría
  nombrar una sola página.
- La comprobación de que la limpieza no altera el mapa de páginas se hace **por Volumen**.
- La cabecera que precede a cada Fragmento al vectorizarse sigue llevando **Obra y
  Universo**, no Volumen: para recuperar interesa que los cuatro Volúmenes de *El Señor de
  los Anillos* tiren juntos. El Volumen viaja como metadato del Fragmento, que es de donde
  sale la Cita.
- En `eval/conjunto-evaluacion.yaml` el campo se llama `obra` pero contiene el nombre de un
  **Volumen**. El fichero está congelado y no se toca; quien escriba el ejecutor del ticket
  06 tiene que saberlo.
- El término pasa a llamarse **Tipo de Texto**. Se llamaba «Tipo de Obra», y ese nombre
  apuntaba al dueño equivocado justo en el punto que este ADR viene a separar: la Obra no
  lo lleva, lo lleva el Volumen. Un glosario que nombra mal al dueño de un atributo enseña
  a colgarlo del sitio equivocado.

## Cuándo reconsiderarlo

Si el Corpus dejara de tener Obras repartidas en varios ficheros —hoy sólo *El Señor de los
Anillos*—, el nivel de Volumen sobraría y podría plegarse otra vez sobre la Obra. La única
forma de que eso ocurra es que *El Señor de los Anillos* salga del Corpus, así que no es
previsible.

Si en algún momento los cuatro ficheros se sustituyen por una edición con numeración
continua, el Volumen deja de hacer falta para desambiguar la página — pero sigue haciendo
falta para el Tipo de Texto, que es lo que distingue los *Apéndices* de los tres tomos.
